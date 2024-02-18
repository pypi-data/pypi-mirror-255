# vim: ts=4:sts=4:sw=4
#
# @date 2020-12-20
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
import numpy.typing
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import ReaderResult, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'time_dependent'

flags = {'no_qc_performed': 0,
         'good_data': 1,
         'probably_good_data': 2,
         'bad_data_that_are_potentially_correctable': 3,
         'bad_data': 4,
         'value_changed': 5,
         'not_used': 6,
         'nominal_value': 7,
         'interpolated_value': 8,
         'missing_value': 9}


class InputPathMissing(ValueError):
    """Error raised when the input options have no "path" entry"""
    pass


class DepthValueMissing(ValueError):
    """Error raised when the input options have no "depth_value" entry."""
    pass


class DepthShapeNotSupported(Exception):
    """Error raised when the DEPH variable has an unsupported number of
    dimensions (0 or >2)"""
    pass


class NotEnoughData(Exception):
    """Error raised when the input data has less than 3 values, which is the
    minimal values count supported by this reader."""
    def __init__(self) -> None:
        """"""
        msg = 'This reader requires at least three along-track values'
        super(NotEnoughData, self).__init__(msg)


class InvalidDepthValue(Exception):
    """Error raised when the value passed as "depth_value" input option is not
    a valid float."""
    def __init__(self, str_value: str) -> None:
        """"""
        self.str_value = str_value
        msg = f'"{str_value}" cannot be converted into a numerical depth value'
        super(InvalidDepthValue, self).__init__(msg)


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           '    depth_value\tDepth of the drifter trajectory to convert',
           '    with-temperature\tRead temperature variable (yes)',
           '    with-day\tInclude day as a variable (yes)',)
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def mask_data(lon_mask: numpy.typing.NDArray, lat_mask: numpy.typing.NDArray,
              time_mask: numpy.typing.NDArray,
              pos_qc: numpy.typing.NDArray,
              time_qc: numpy.typing.NDArray
              ) -> numpy.typing.NDArray:
    list_bad_flags = ('bad_data_that_are_potentially_correctable', 'bad_data',
                      'missing_value')

    off_flags = numpy.uint32(0)
    for nflag in list_bad_flags:
        off_flags = off_flags + numpy.uint32(1 << flags[nflag])

    mask_on = (~lon_mask & ~ lat_mask & ~time_mask)

    # Valid mask = values are not masked and QC must have bad flags set to 0
    mask_on = (mask_on & (numpy.bitwise_and(time_qc, off_flags) == 0))
    mask_on = (mask_on & (numpy.bitwise_and(pos_qc, off_flags) == 0))
    result: numpy.typing.NDArray = numpy.ma.getdata(mask_on)
    return result


def mask_qual(qual: numpy.typing.NDArray
              ) -> numpy.typing.NDArray:
    list_bad_flags = ('bad_data_that_are_potentially_correctable', 'bad_data',
                      'missing_value')
    off_flags = numpy.uint32(0)
    for nflag in list_bad_flags:
        off_flags = off_flags + numpy.uint32(1 << flags[nflag])

    mask_off = numpy.zeros(numpy.shape(qual), dtype='bool')

    # Invalid mask = QC must have bad flags set to 1
    mask_off = (mask_off | (numpy.bitwise_and(qual, off_flags) > 0))

    result: numpy.typing.NDArray = numpy.ma.getdata(~mask_off)
    return result


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
    variables = {'TEMP': {'name': 'temperature',
                          'long_name': 'Temperature',
                          'units': 'K',
                          'valid_min': 273.15,
                          'valid_max': 315.5,
                          'options': {}},
                 'EWCT': {'name': 'eastward_velocity',
                          'long_name': 'Eastward velocity',
                          'units': 'm.s-1',
                          'valid_min': -2.0,
                          'valid_max': 2.0,
                          'options': {}},
                 'NSCT': {'name': 'northward_velocity',
                          'long_name': 'Northward velocity',
                          'units': 'm',
                          'valid_min': -2.0,
                          'valid_max': 2.0,
                          'options': {}},
                 }
    dic_max = {}
    dic_min = {}
    # initialize valid min and max in a separate dictionary
    for var_id in variables.keys():
        dic_max[var_id] = variables[var_id]['valid_max']
        dic_min[var_id] = variables[var_id]['valid_min']
    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    # Read depth from input options
    _depth_value = input_opts.get('depth_value', None)
    if _depth_value is None:
        raise DepthValueMissing()

    try:
        depth_value = float(_depth_value)
    except ValueError:
        raise InvalidDepthValue(_depth_value)
    depth_str = f'{depth_value}'.rstrip('0').rstrip('.')

    _include_temp = input_opts.get('with-temperature', 'yes')
    include_temp = (_include_temp.lower() in ('yes', 'true', '1'))
    if include_temp is False:
        variables.pop('TEMP')

    _include_day = input_opts.get('with-day', 'yes')
    include_day = (_include_day.lower() in ('yes', 'true', '1'))

    # Define depth for all variables
    for var_id in variables.keys():
        variables[var_id]['depth'] = f'{depth_str}m'

    granule.vars = variables
    channels = list(variables.keys())

    lon_name = 'LONGITUDE'
    lat_name = 'LATITUDE'
    time_name = 'TIME'
    depth_name = 'DEPH'
    spatial_res_meters = 1.e07

    f_handler = netCDF4.Dataset(input_path, 'r')
    _time = idf_converter.lib.extract_variable_values(f_handler, time_name)
    _lon = idf_converter.lib.extract_variable_values(f_handler, lon_name)
    _lat = idf_converter.lib.extract_variable_values(f_handler, lat_name)
    _dep = idf_converter.lib.extract_variable_values(f_handler, depth_name)
    _pos_qc = f_handler.variables['POSITION_QC'][:]
    _time_qc = f_handler.variables[f'{time_name}_QC'][:]
    _tunits = f_handler.variables[time_name].units
    date = netCDF4.num2date(_time, units=_tunits)

    _lon_mask = numpy.ma.getmaskarray(_lon)
    if _lon_mask.any():
        logger.warning(f'Masked longitudes in {input_path}')
    _lon = numpy.ma.getdata(_lon)

    _lat_mask = numpy.ma.getmaskarray(_lat)
    if _lat_mask.any():
        logger.warning(f'Masked latitudes in {input_path}')
    _lat = numpy.ma.getdata(_lat)

    _time_mask = numpy.ma.getmaskarray(_time)
    if _time_mask.any():
        logger.warning(f'Masked times in {input_path}')
    _time = numpy.ma.getdata(_time)

    # mask non valid position / time
    _mask = mask_data(_lon_mask, _lat_mask, _time_mask, _pos_qc, _time_qc)
    if not _mask.any():
        logger.warning(f'No valid data in "{input_path}"')
        f_handler.close()
        raise idf_converter.lib.EarlyExit()

    # Only keep valid coordinates
    valid_ind = numpy.where(_mask)
    _time = _time[valid_ind] * 86400
    _lon = _lon[valid_ind]
    _lat = _lat[valid_ind]
    date = date[valid_ind]

    # Cut trajectory when geospatial or temporal information or missing
    dt = _time[1:] - _time[: -1]
    _ind = numpy.where(dt > 7 * 3600)[0]
    if _ind.any():
        for i in sorted(_ind, reverse=True):
            _lon = numpy.insert(_lon, i + 1, _lon[i + 1])
            _lon = numpy.insert(_lon, i + 1, _lon[i])
            _lat = numpy.insert(_lat, i + 1, _lat[i + 1])
            _lat = numpy.insert(_lat, i + 1, _lat[i])
            _time = numpy.insert(_time, i + 1, _time[i + 1] - 1)
            _time = numpy.insert(_time, i + 1, _time[i] + 1)
            date = numpy.insert(date, i + 1, date[i + 1])
            date = numpy.insert(date, i + 1, date[i])

    initial_size = _mask.shape[0]
    final_size = _time.shape[0]

    _dic: typing.Dict[str, numpy.typing.NDArray] = {}
    for var_id in granule.vars.keys():
        if var_id not in f_handler.variables.keys():
            tmp_data = numpy.full(final_size, numpy.nan, dtype=numpy.float32)
            granule.vars[var_id]['datatype'] = tmp_data.dtype
            _dic[var_id] = numpy.ma.masked_invalid(tmp_data)
            continue
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        qual_id = f'{var_id}_QC'
        qual = idf_converter.lib.extract_variable_values(f_handler, qual_id)

        _mask_qual = mask_qual(qual)
        band[~_mask_qual] = numpy.nan

        depth_ind = numpy.where(_dep == depth_value)
        if 0 >= len(depth_ind[0]):
            logger.warning(f'{var_id} not available at {depth_str}m depth '
                           f'in "{input_path}"')
            tmp_data = numpy.full(final_size, numpy.nan, dtype=numpy.float32)
            granule.vars[var_id]['datatype'] = tmp_data.dtype
            _dic[var_id] = numpy.ma.masked_invalid(tmp_data)
            continue

        if 2 == len(_dep.shape):
            # format before 2023-11-30: DEPH(TIME, DEPTH)
            _band1d = numpy.full(initial_size, numpy.nan, dtype=band.dtype)
            _band1d[depth_ind[0]] = band[depth_ind]
        elif 1 == len(_dep.shape):
            # format starting 2023-11-30: DEPH(DEPTH)
            _band1d = band[:, depth_ind]
        else:
            raise DepthShapeNotSupported()

        _band1d = _band1d[valid_ind]

        if _ind.any():
            for i in sorted(_ind, reverse=True):
                _band1d = numpy.insert(_band1d, i + 1, numpy.nan)
                _band1d = numpy.insert(_band1d, i + 1, numpy.nan)
        granule.vars[var_id]['datatype'] = band.dtype
        _dic[var_id] = numpy.ma.masked_invalid(_band1d)
    f_handler.close()

    # Compute Norm speed as SEAScope do not compute norm for trajectories yet
    nsct_mask = numpy.ma.getmaskarray(_dic['NSCT'])
    ewct_mask = numpy.ma.getmaskarray(_dic['EWCT'])
    _mask_finite = (~nsct_mask & ~ewct_mask)
    nsct_sqr: numpy.typing.NDArray = _dic['NSCT']**2
    ewct_sqr: numpy.typing.NDArray = _dic['EWCT']**2
    _speed = numpy.sqrt(nsct_sqr + ewct_sqr, where=_mask_finite)
    _speed[numpy.ma.getmaskarray(_speed)] = numpy.nan
    _dic['speed'] = numpy.ma.masked_invalid(_speed)

    max_speed = 0.0
    if not numpy.isnan(_dic['speed']).all():
        max_speed = numpy.nanmax(_dic['speed'])
    granule.vars['speed'] = {'name': 'speed',
                             'long_name': 'velocity norm',
                             'units': 'm/s',
                             'valid_min': 0,
                             'valid_max': max_speed,
                             'depth': f'{depth_str}m',
                             'datatype': granule.vars['NSCT']['datatype'],
                             'options': {}}
    channels.append('speed')
    dic_max['speed'] = max_speed
    dic_min['speed'] = 0

    # Translate Celsius into Kelvin
    if include_temp:
        valid_temp_ind = numpy.where(numpy.isfinite(_dic['TEMP']))
        if numpy.all((-10.0 < _dic['TEMP'][valid_temp_ind]) &
                     (100 > _dic['TEMP'][valid_temp_ind])):
            _dic['TEMP'][valid_temp_ind] = (273.15 +
                                            _dic['TEMP'][valid_temp_ind])

    # Add coordinates variables
    granule.vars['lat'] = {'units': 'degrees north',
                           'datatype': _lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'units': 'degrees east',
                           'datatype': _lon.dtype,
                           'options': {}
                           }
    _dic['lon'] = _lon
    _dic['lat'] = _lat

    # Apply time offset to transform time into an EPOCH timestamp
    ref_time = datetime.datetime(1950, 1, 1)
    epoch = datetime.datetime(1970, 1, 1)
    time_offset = (ref_time - epoch).total_seconds()
    shifted_time: numpy.typing.NDArray = _time + time_offset
    granule.vars['time'] = {'units': 'seconds since 1970-01-01T00:00:00.000Z',
                            'datatype': numpy.double,
                            'options': {}}
    _dic['time'] = shifted_time.astype(numpy.double)

    # Store day in month as SEAScope do not show position in time yet
    if include_day:
        # Store day in month as SEAScope do not show position in time yet
        dayinmonth = numpy.array([x.day for x in date])

        granule.vars['day'] = {'name': 'day_in_month',
                               'units': 'day in month',
                               'valid_min': 1,
                               'valid_max': 31,
                               'options': {}}
        _dic['day'] = dayinmonth
        channels.append('day')

    # Set Global parameters
    granule_name = os.path.splitext(os.path.basename(input_path))[0]
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_res_meters
    granule.meta['idf_spatial_resolution_units'] = 'm'

    # Split in monthly file to display only part of the trajectory in SEAScope
    list_yearmonth = [f'{x.year:04d}{x.month:02d}' for x in date]
    for ym in set(list_yearmonth):
        _ind_time = numpy.where(numpy.array(list_yearmonth) == f'{ym}')[0]
        # Get the monthly data plus the next index to have continuous
        # trajectories
        _slice = slice(_ind_time[0], _ind_time[-1] + 2)

        # ... unless there is actually a discontinuity
        if numpy.ma.getmaskarray(_dic['NSCT'])[_ind_time[-1]] is True:
            _slice = slice(_ind_time[0], _ind_time[-1] + 1)

        for var_id in granule.vars.keys():
            granule.vars[var_id]['array'] = _dic[var_id][_slice]
            if var_id in dic_min.keys():
                granule.vars[var_id]['valid_min'] = dic_min[var_id]
            if var_id in dic_max.keys():
                granule.vars[var_id]['valid_max'] = dic_max[var_id]

        # Trick to deal with continuity in longitude
        lonc: numpy.typing.NDArray = _dic['lon'][_slice]
        lonc_valid = lonc[numpy.where(numpy.isfinite(lonc))]
        lref = lonc_valid[int(0.5 * numpy.shape(lonc_valid)[0])]
        fixed_lon = numpy.mod(lonc - (lref - 180.), 360.) + (lref - 180.)
        granule.vars['lon']['array'] = fixed_lon

        granule.dims['time'] = numpy.size(granule.vars['time']['array'])
        _convertutc = datetime.datetime.utcfromtimestamp
        time_array: numpy.typing.NDArray = _dic['time'][_slice]
        start_dt = _convertutc(time_array[0])
        stop_dt = _convertutc(time_array[-1])
        if ym not in granule_name:
            _granule_name = f'{granule_name}_{ym}'
        else:
            _granule_name = granule_name
        granule.meta['idf_granule_id'] = f'{_granule_name}'
        granule.meta['time_coverage_start'] = start_dt
        granule.meta['time_coverage_end'] = stop_dt

        transforms: TransformsList = []

        transforms.append(('remove_extra_lon_degrees', {'lon_name': 'lon'}))

        output_opts['__export'] = channels

        # data_model, dims, vars, attrs, formatter_jobs
        yield (input_opts, output_opts, granule, transforms)
