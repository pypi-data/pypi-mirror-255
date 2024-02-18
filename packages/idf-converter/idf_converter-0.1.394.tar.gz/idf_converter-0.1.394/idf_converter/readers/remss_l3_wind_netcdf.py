# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-07
#
# This file is part of IDF converter, a set of tools to convert satellite,
# in-situ and numerical model data into Intermediary Data Format, making them
# compatible with the SEAScope application.
#
# Copyright (C) 2014-2022 OceanDataLab
#
# IDF converter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# IDF converter is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IDF converter. If not, see <https://www.gnu.org/licenses/>.

"""
"""

import os
import numpy
import typing
import netCDF4
import logging
import datetime
import scipy.signal
import numpy.typing
import idf_converter.lib
import idf_converter.lib.geo
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import TransformsList, Granule

logger = logging.getLogger(__name__)

DATA_MODEL = idf_converter.readers.netcdf_grid_latlon.DATA_MODEL
WindConfig = typing.Dict[str, typing.Dict[str, str]]
WindVariables = typing.Tuple[typing.List[str], WindConfig]
MutableIndexSlices = typing.List[typing.Union[int, slice]]
IndexSlices = typing.Sequence[typing.Union[int, slice]]
SPEED_VARS = ('wind', 'wind_speed_LF', 'wind_speed_MF', 'wind_speed_AW',
              'wind_speed_TC')


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


class TimeUnitsNotSupported(Exception):
    """Error raised when the units of the time variable are not support by this
    reader."""
    def __init__(self, time_units: str) -> None:
        self.time_units = time_units


class InvalidWindVariable(ValueError):
    """Error raised when the value passed to the wind_variables option does not
    match the expected pattern."""
    def __init__(self, value: str) -> None:
        self.wind_variables_str = value


class NoValidMinute(Exception):
    """Error raised when splitting into swaths is impossible due to the lack
    of valid values in the minutes array."""
    pass


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('    split-swaths\tSet to yes|true|1 if the converter should create'
           ' one output file for each swath (simulating a gridded L2) instead'
           ' of the original data structure (one file containing all swaths)',
           )
    return ('\n'.join(inp), '\t'.join(out))


def get_wind_transforms(output_opts: OutputOptions,
                        wind_vars: WindConfig,
                        original_var_ids: typing.List[str],
                        has_asc_desc: bool,
                        ) -> TransformsList:
    """"""
    # Add transform for converting (module, dir) to (eastward, northward)
    transforms: TransformsList = []

    to_remove = []
    vec_cfg = {}
    for wind_var_id, wind_var_cfg in wind_vars.items():
        speed_var_id = wind_var_cfg['speed']
        dir_var_id = wind_var_cfg['direction']

        if has_asc_desc:
            speed_asc_id = f'{speed_var_id}_asc'
            if speed_asc_id not in original_var_ids:
                to_remove.append(speed_asc_id)

            speed_desc_id = f'{speed_var_id}_desc'
            if speed_desc_id not in original_var_ids:
                to_remove.append(speed_desc_id)

            dir_asc_id = f'{dir_var_id}_asc'
            if dir_asc_id not in original_var_ids:
                to_remove.append(dir_asc_id)

            dir_desc_id = f'{dir_var_id}_desc'
            if dir_desc_id not in original_var_ids:
                to_remove.append(dir_desc_id)

            vec_cfg[f'{wind_var_id}_asc'] = {'direction': dir_asc_id,
                                             'module': speed_asc_id,
                                             'radians': False,
                                             'angle_to_east': numpy.pi / 2.0,
                                             'clockwise': True,
                                             'meteo': False}
            vec_cfg[f'{wind_var_id}_desc'] = {'direction': dir_desc_id,
                                              'module': speed_desc_id,
                                              'radians': False,
                                              'angle_to_east': numpy.pi / 2.0,
                                              'clockwise': True,
                                              'meteo': False}
        else:
            if speed_var_id not in original_var_ids:
                to_remove.append(speed_var_id)

            if dir_var_id not in original_var_ids:
                to_remove.append(dir_var_id)

            vec_cfg[wind_var_id] = {'direction': dir_var_id,
                                    'module': speed_var_id,
                                    'radians': False,
                                    'angle_to_east': numpy.pi / 2.0,
                                    'clockwise': True,
                                    'meteo': False}

    wind_targets = list(vec_cfg.keys())
    to_remove = list(set(to_remove))

    if 0 < len(wind_targets):
        # Add eastward_ and northward_ variables to the export targets
        targets = output_opts['__export']

        for wind_var_id in wind_targets:
            targets.append(f'eastward_{wind_var_id}')
            targets.append(f'northward_{wind_var_id}')

        transforms.append(('dir2vectors', {'targets': wind_targets,
                                           'configs': vec_cfg}))

    if 0 < len(to_remove):
        # If eastward/northward variables carry the wind speed and direction
        # information so there is no need to keep it in the output
        transforms.append(('remove_vars', {'targets': to_remove}))

    return transforms


def create_granule(input_opts: InputOptions,
                   output_opts: OutputOptions,
                   pass_suffix: str,
                   start_dt: datetime.datetime,
                   stop_dt: datetime.datetime,
                   spatial_resolution: float,
                   lat: numpy.typing.NDArray,
                   lon: numpy.typing.NDArray,
                   values: typing.Dict[str, numpy.typing.NDArray],
                   units: typing.Dict[str, str],
                   ) -> Granule:
    """"""
    # Format granule
    granule_name, _ = os.path.splitext(os.path.basename(input_opts['path']))

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    _swath_granule_name = f'{granule_name}_{start_dt:%H%M}_{stop_dt:%H%M}'
    _granule_name = f'{_swath_granule_name}{pass_suffix}'
    granule.meta['idf_granule_id'] = _granule_name

    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_resolution
    granule.meta['idf_spatial_resolution_units'] = 'm'

    for var_id, var_values in values.items():
        var_units = units.get(var_id, '')
        granule.vars[var_id] = {'array': var_values,
                                'name': var_id,
                                'units': var_units,
                                'valid_min': numpy.nanmin(var_values),
                                'valid_max': numpy.nanmax(var_values),
                                'datatype': var_values.dtype,
                                'options': {}}

    _lon, trunc_to_0 = idf_converter.lib.mod360(lon - lon[0], 9)
    _lon = _lon + lon[0]

    if trunc_to_0 is True:
        logger.warning('Some longitude values very close to 0 degrees have '
                       'been truncated to 0 to avoid underflow errors')

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': _lon,
                           'units': 'degrees_east',
                           'datatype': _lon.dtype,
                           'options': {}}
    granule.dims['lat'] = lat.size
    granule.dims['lon'] = lon.size

    return granule


def get_swath_minute_bounds(minute: numpy.typing.ArrayLike,
                            min_swath_duration: int = 80
                            ) -> typing.Tuple[numpy.typing.NDArray,
                                              numpy.typing.NDArray]:
    """"""
    valid_minute = minute.compressed()
    if valid_minute.size == 0:
        raise NoValidMinute()
    hist, _ = numpy.histogram(valid_minute, bins=1441, range=(0, 1441))

    valid_index = numpy.where(hist > 0)[0]
    valid_index.sort()

    # Compute mode for minute differences in order to identify actual gaps
    # later on
    dminute, count = numpy.unique(valid_index[1:] - valid_index[:-1],
                                  return_counts=True)
    nominal_dminute = dminute[count.argmax()]

    # Smoothen the histogram to remove little gaps
    span = 10
    smooth_hist = numpy.convolve(hist,
                                 numpy.ones(span * 2 + 1) / (span * 2 + 1),
                                 mode="same")

    # Find indexes of local minima on the smooth histogram
    smooth_min_index, _ = scipy.signal.find_peaks(-1 * smooth_hist,
                                                  distance=min_swath_duration)

    # Compute local minima on the actual histogram
    _minute0 = [valid_index[0]]
    _minute1 = []
    for i in range(0, smooth_min_index.size):
        smooth_index = smooth_min_index[i]

        # The index of the local min in the smoothed histogram might be a bin
        # with a 0 count in the original histogram so we need to get the index
        # of the closest non empty bin
        closest_data_index = numpy.searchsorted(valid_index, smooth_index)
        hist_index = valid_index[closest_data_index]

        prev_mask = (valid_index < hist_index)
        valid_prev = numpy.array([])
        if prev_mask.any():
            valid_prev = valid_index[numpy.where(prev_mask)]
        next_mask = (valid_index > hist_index)
        valid_next = numpy.array([])
        if next_mask.any():
            valid_next = valid_index[numpy.where(next_mask)]

        # Make sure local min in the smoothed histogram is also a local min in
        # the original histogram
        prev_index = hist_index
        if 0 < valid_prev.size:
            prev_index = valid_prev[-1]

        next_index = hist_index
        if 0 < valid_next.size:
            next_index = valid_next[0]

        prev_dist = hist_index - prev_index
        next_dist = next_index - hist_index
        if 2 * nominal_dminute < prev_dist + next_dist:
            hist_index = prev_index
        else:
            closer_to_prev = (prev_dist < next_dist)
            closer_to_next = (prev_dist > next_dist)
            equidistant = (prev_dist == next_dist)
            prev_value = hist[prev_index]
            next_value = hist[next_index]
            if closer_to_prev or (equidistant and (prev_value < next_value)):
                # Check left
                _smaller_mask = (hist[valid_prev] < hist[hist_index])
                smaller_mask = numpy.cumprod(_smaller_mask[::-1])[::-1]
                if (0 < smaller_mask).any():
                    hist_index = valid_prev[numpy.where(smaller_mask)].min()
            elif closer_to_next or (equidistant and (next_value < prev_value)):
                # Check right
                _smaller_mask = (hist[valid_next] < hist[hist_index])
                smaller_mask = numpy.cumprod(_smaller_mask)
                if (0 < smaller_mask).any():
                    hist_index = valid_next[numpy.where(smaller_mask)].max()

        _minute1.append(hist_index)

        next_mask = (valid_index > hist_index)
        if next_mask.any():
            m0_index = valid_index[numpy.where(next_mask)].min()
            _minute0.append(m0_index)

    minute0 = numpy.array(_minute0)
    if len(_minute0) > len(_minute1):
        minute1 = numpy.concatenate([_minute1, [valid_index[-1]]])
    else:
        minute1 = numpy.array(_minute1)

    return minute0, minute1


def split_swaths(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 original_var_ids: typing.List[str],
                 day: datetime.datetime,
                 minute: numpy.typing.ArrayLike,
                 lat: numpy.typing.NDArray,
                 lon: numpy.typing.NDArray,
                 pass_suffix: str,
                 values: typing.Dict[str, numpy.typing.NDArray],
                 units: typing.Dict[str, str],
                 wind_vars: WindConfig
                 ) -> typing.Iterator[ReaderResult]:
    """"""
    nlon = lon.size

    minute0, minute1 = get_swath_minute_bounds(minute)

    # Extract mask for the first speed variable found in SPEED_VARS
    wind_mask = numpy.full(minute.shape, False, dtype='bool')
    for var_id in SPEED_VARS:
        if var_id in values:
            wind_mask = numpy.ma.getmaskarray(values[var_id])
            break

    dlat = lat[1:] - lat[:-1]
    dlon = lon[1:] - lon[:-1]
    spatial_resolution = min([abs(dlat.mean()), abs(dlon.mean())]) * 111000.

    concat: typing.Callable[[typing.Sequence[numpy.typing.ArrayLike],
                             typing.Optional[int]],
                            numpy.typing.ArrayLike]
    concat = numpy.ma.concatenate
    for _minute0, _minute1 in zip(minute0, minute1):
        indpass = numpy.where((minute >= _minute0) &
                              (minute <= _minute1) &
                              (~wind_mask))

        if indpass[0].size == 0:
            continue
        if indpass[0].min() == indpass[0].max():
            logger.warning('Skipping swath containing a single latitude')
            continue

        lat_slice = slice(indpass[0].min(), indpass[0].max() + 1)
        swath_lat = lat[lat_slice]

        indlon = numpy.unique(indpass[1])
        if indlon.size == 1:
            dindlon = numpy.array([0])
        else:
            dindlon = indlon[1:] - indlon[:-1]

        swath_values = {}
        if (indlon[-1] - indlon[0]) <= (nlon - dindlon.max()):
            lon_slice = slice(indlon[0], indlon[-1] + 1)
            swath_lon = lon[lon_slice]
            swath_minute = minute[lat_slice, lon_slice].copy()
            for var_id, var_values in values.items():
                swath_values[var_id] = var_values[lat_slice, lon_slice].copy()
        else:
            indsplit = dindlon.argmax()
            lon_slice0 = slice(indlon[indsplit + 1], nlon)
            lon_slice1 = slice(0, indlon[indsplit] + 1)
            swath_lon = concat((lon[lon_slice0], lon[lon_slice1]), axis=0)
            swath_minute = concat((minute[lat_slice, lon_slice0],
                                   minute[lat_slice, lon_slice1]),
                                  axis=1)
            for var_id, var_values in values.items():
                slice0_values = var_values[lat_slice, lon_slice0]
                slice1_values = var_values[lat_slice, lon_slice1]
                swath_values[var_id] = concat((slice0_values, slice1_values),
                                              axis=1)

        before_ind = numpy.where(swath_minute < _minute0)
        after_ind = numpy.where(swath_minute > _minute1)
        for var_id, var_values in swath_values.items():
            var_values[before_ind] = numpy.ma.masked
            var_values[after_ind] = numpy.ma.masked

        start_dt = day + datetime.timedelta(seconds=int(_minute0 * 60))
        stop_dt = day + datetime.timedelta(seconds=int(_minute1 * 60))
        granule = create_granule(input_opts, output_opts, pass_suffix,
                                 start_dt, stop_dt, spatial_resolution,
                                 swath_lat, swath_lon, swath_values, units)

        output_opts['__export'] = list(swath_values.keys())

        # Add transforms
        transforms = get_wind_transforms(output_opts, wind_vars,
                                         original_var_ids, False)

        yield input_opts, output_opts, granule, transforms


def parse_wind_vars(input_opts: InputOptions
                    ) -> WindVariables:
    """"""
    required_vars: typing.List[str] = []
    wind_vars: WindConfig = {}
    _wind_vars = input_opts.get('wind_variables', None)
    if _wind_vars is None:
        return (required_vars, wind_vars)

    for wind_cfg_str in _wind_vars.split(','):
        if 0 >= len(wind_cfg_str.strip()):
            continue

        wind_cfg_elements = wind_cfg_str.split(':')
        if 3 == len(wind_cfg_elements):
            output_var_id, speed_var_id, direction_var_id = wind_cfg_elements
            wind_vars[output_var_id] = {'speed': speed_var_id,
                                        'direction': direction_var_id}
            required_vars.append(speed_var_id)
            required_vars.append(direction_var_id)
        else:
            raise InvalidWindVariable(wind_cfg_str)

    return (list(set(required_vars)), wind_vars)


def compute_slices(variable: netCDF4.Variable,
                   pass_dim_id: str
                   ) -> typing.Tuple[IndexSlices, IndexSlices]:
    """Compute data slices assuming all variables have the same dimensions"""
    asc_slices: MutableIndexSlices = []
    desc_slices: MutableIndexSlices = []
    for dim_id in variable.dimensions:
        if dim_id == pass_dim_id:
            asc_slices.append(0)
            desc_slices.append(1)
        else:
            asc_slices.append(slice(None, None, None))
            desc_slices.append(slice(None, None, None))

    return asc_slices, desc_slices


def split_ascending_descending(input_opts: InputOptions,
                               output_opts: OutputOptions,
                               original_var_ids: typing.List[str],
                               day: datetime.datetime,
                               minutes: numpy.typing.NDArray,
                               lon_var_id: str,
                               lat_var_id: str,
                               values: typing.Dict[str, numpy.typing.NDArray],
                               units: typing.Dict[str, str],
                               wind_vars: WindConfig,
                               asc_slices: IndexSlices,
                               desc_slices: IndexSlices
                               ) -> typing.Iterator[ReaderResult]:
    """"""
    # Format extracted data into input options before passing them to the
    # generic netCDF latlon grid reader
    input_opts['lon_variable'] = lon_var_id
    input_opts['lat_variable'] = lat_var_id

    var_ids_by_pass = []
    input_opts['extra_values'] = {}
    for var_id in values.keys():
        var_units = units.get(var_id, '')

        asc_values = values[var_id][asc_slices]
        input_opts['extra_values'][f'{var_id}_asc'] = {'array': asc_values,
                                                       'units': var_units,
                                                       'dims': ['lat', 'lon']}

        desc_values = values[var_id][desc_slices]
        input_opts['extra_values'][f'{var_id}_desc'] = {'array': desc_values,
                                                        'units': var_units,
                                                        'dims': ['lat', 'lon']}
        var_ids_by_pass.append(f'{var_id}_asc')
        var_ids_by_pass.append(f'{var_id}_desc')

    input_opts['variables'] = ','.join(var_ids_by_pass)

    # Time coverage
    start_minutes = int(minutes.min())
    start_dt = day + datetime.timedelta(seconds=start_minutes * 60)
    start_str = f'time_coverage_start:"{start_dt:%Y-%m-%dT%H:%M:%SZ}"'

    stop_minutes = int(minutes.max())
    stop_dt = day + datetime.timedelta(seconds=stop_minutes * 60)
    stop_str = f'time_coverage_end:"{stop_dt:%Y-%m-%dT%H:%M:%SZ}"'

    input_opts['global_overrides'] = ','.join([start_str, stop_str])
    del input_opts['time_variable']  # Global attributes provide time coverage

    generic_latlon_grid = idf_converter.readers.netcdf_grid_latlon
    generic = generic_latlon_grid.read_data(input_opts, output_opts)
    input_opts, output_opts, granule, transforms = next(generic)

    # Add transform for converting (module, dir) to (eastward, northward)
    to_remove = []
    vec_cfg = {}
    for wind_var_id, wind_var_cfg in wind_vars.items():
        speed_var_id = wind_var_cfg['speed']
        dir_var_id = wind_var_cfg['direction']

        to_remove.append(f'{speed_var_id}_asc')
        to_remove.append(f'{speed_var_id}_desc')
        to_remove.append(f'{dir_var_id}_asc')
        to_remove.append(f'{dir_var_id}_desc')

        vec_cfg[f'{wind_var_id}_asc'] = {'direction': f'{dir_var_id}_asc',
                                         'module': f'{speed_var_id}_asc',
                                         'radians': False,
                                         'angle_to_east': numpy.pi / 2.0,
                                         'clockwise': True,
                                         'meteo': False}
        vec_cfg[f'{wind_var_id}_desc'] = {'direction': f'{dir_var_id}_desc',
                                          'module': f'{speed_var_id}_desc',
                                          'radians': False,
                                          'angle_to_east': numpy.pi / 2.0,
                                          'clockwise': True,
                                          'meteo': False}
    wind_targets = list(vec_cfg.keys())

    if 0 < len(wind_targets):
        # Add eastward_ and northward_ variables to the export targets
        targets = output_opts['__export']

        for wind_var_id in wind_targets:
            targets.append(f'eastward_{wind_var_id}')
            targets.append(f'northward_{wind_var_id}')

        transforms.append(('dir2vectors', {'targets': wind_targets,
                                           'configs': vec_cfg}))

        # If eastward/northward variables carry the wind speed and direction
        # information so there is no need to keep it in the output
        transforms.append(('remove_vars', {'targets': to_remove}))

    yield input_opts, output_opts, granule, transforms


def read_data(input_opts: InputOptions,
              output_opts: OutputOptions
              ) -> typing.Iterator[ReaderResult]:
    """Read input file, extract data and metadata, store them in a Granule
    object then prepare formatting instructions to finalize the conversion to
    IDF format.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule, list)
        A tuple which contains four elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the extracted information
          has been stored

        - a :obj:list of :obj:dict describing the formatting operations that
          the converter must perform before serializing the result in IDF
          format
    """
    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    pass_dim_id = input_opts.get('pass_dimension', 'node')
    lat_var_id = input_opts.get('lat_variable', 'lat')
    lon_var_id = input_opts.get('lon_variable', 'lon')
    time_var_id = input_opts.get('time_variable', 'minute')

    variables = input_opts.get('variables', 'wind')
    original_var_ids = [_.strip() for _ in variables.split(',')
                        if 0 < len(_.strip())]

    required_var_ids, wind_vars = parse_wind_vars(input_opts)

    var_ids = original_var_ids + required_var_ids
    var_ids = list(set(var_ids))
    if 0 >= len(var_ids):
        logger.warning('No variable to extract')
        raise idf_converter.lib.EarlyExit()

    # Read variables
    f_handler = netCDF4.Dataset(input_path, 'r')

    lon = f_handler.variables[lon_var_id][:]
    lat = f_handler.variables[lat_var_id][:]
    time_units = f_handler.variables[time_var_id].units
    time_values = f_handler.variables[time_var_id][:]

    values = {}
    units = {}
    for var_id in var_ids:
        # The valid_min and valid_max attributes are incorrect, causing masking
        # issues. Here we disable netCDF auto-masking for this variable as a
        # workaround.
        f_handler.variables[var_id].set_auto_mask(False)
        _values = f_handler.variables[var_id][:]
        units[var_id] = f_handler.variables[var_id].units
        if var_id in SPEED_VARS:
            # Mask negative values for wind speed
            values[var_id] = numpy.ma.masked_less(_values, 0)
        else:
            values[var_id] = _values

    # Get temporal coverage
    day_attr_name = 'day_of_month_of observation'
    if hasattr(f_handler, day_attr_name):
        day = datetime.datetime(f_handler.year_of_observation,
                                f_handler.month_of_observation,
                                f_handler.getncattr(day_attr_name))
    else:
        day = datetime.datetime(f_handler.year_of_observation,
                                f_handler.month_of_observation,
                                f_handler.day_of_month_of_observation)

    # Compute slices for ascending and descending passes assuming all variables
    # have the same dimensions
    _asc_slices, _desc_slices = compute_slices(f_handler.variables[var_ids[0]],
                                               pass_dim_id)
    f_handler.close()

    asc_slices = tuple(_asc_slices)
    desc_slices = tuple(_desc_slices)

    # Convert time to minutes
    if 'minute' in time_units:
        minutes = time_values
    elif 'hour' in time_units:
        minutes = time_values * 60
    else:
        raise TimeUnitsNotSupported(time_units)

    use_swaths_splitting = output_opts.get('split-swaths', 'n')
    if use_swaths_splitting.lower() in ('1', 'y', 'yes'):
        pass_minutes = minutes[asc_slices]
        asc_values = {}
        for var_id, var_values in values.items():
            asc_values[var_id] = var_values[asc_slices]
        yield from split_swaths(input_opts, output_opts, original_var_ids,
                                day, pass_minutes, lat, lon, '_asc',
                                asc_values, units, wind_vars)

        pass_minutes = minutes[desc_slices]
        desc_values = {}
        for var_id, var_values in values.items():
            desc_values[var_id] = var_values[desc_slices]
        yield from split_swaths(input_opts, output_opts, original_var_ids,
                                day, pass_minutes, lat, lon, '_desc',
                                desc_values, units, wind_vars)
    else:
        yield from split_ascending_descending(input_opts, output_opts,
                                              original_var_ids, day, minutes,
                                              lon_var_id, lat_var_id, values,
                                              units, wind_vars, asc_slices,
                                              desc_slices)
