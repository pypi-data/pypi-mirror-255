# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-25
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
from idf_converter.lib.types import ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'time_dependent'


class InputPathMissing(ValueError):
    """Error raised when the input options have no "path" entry"""
    pass


class FrequencyNotSupported(ValueError):
    """Error raised when the requested frequency is neither 1Hz nor 20Hz, the
    only frequencies available in the input files."""
    def __init__(self, frequency: int) -> None:
        """"""
        self.frequency = frequency
        msg = 'This reader only supports 1Hz and 20Hz data'
        super(FrequencyNotSupported, self).__init__(msg)


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           '    frequency\tEither 1 or 20 (1Hz by default)',)
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def mask_ssha(var_dicts: typing.Dict[str, typing.Any],
              var_id: str
              ) -> numpy.typing.NDArray:
    """Build mask for SSHA.

    Parameters
    ----------
    var_dict: dict
        Dictionary describing the SSHA variable

    Returns
    -------
    numpy.ndarray
        Array with cells set to True where values should be masked , i.e. NaN
        or aberrant values (absolute values above 50m).
    """
    var_dict = var_dicts[var_id]
    values = var_dict['array']
    values._sharedmask = False
    nan_mask = (numpy.isnan(values))
    values[numpy.where(nan_mask)] = var_dict['_FillValue']  # avoid warning
    out_of_range_mask = (numpy.absolute(values) > 50.)
    _mask = (nan_mask | out_of_range_mask)
    result: numpy.typing.NDArray = numpy.ma.getdata(_mask)
    return result


def mask_swh(var_dicts: typing.Dict[str, typing.Any],
             var_id: str
             ) -> numpy.typing.NDArray:
    """Build mask for SWH.

    Parameters
    ----------
    var_dict: dict
        Dictionary describing the SWH variable

    Returns
    -------
    numpy.ndarray
        Array with cells set to True where values should be masked , i.e. NaN
        or aberrant values (absolute values above 50m).
    """
    var_dict = var_dicts[var_id]
    values = var_dict['array']
    values._sharedmask = False
    nan_mask = (numpy.isnan(values))
    values[numpy.where(nan_mask)] = var_dict['_FillValue']  # avoid warning
    out_of_range_mask = (numpy.absolute(values) > 50.)
    _mask = (nan_mask | out_of_range_mask)
    result: numpy.typing.NDArray = numpy.ma.getdata(_mask)
    return result


def mask_sig0(var_dicts: typing.Dict[str, typing.Any],
              var_id: str
              ) -> numpy.typing.NDArray:
    """Build mask for Sigma0.

    Parameters
    ----------
    var_dict: dict
        Dictionary describing the Sigma0 variable

    Returns
    -------
    numpy.ndarray
        Array with cells set to True where values should be masked , i.e. NaN
        or aberrant values (values above 100).
    """
    var_dict = var_dicts[var_id]
    values = var_dict['array']
    values._sharedmask = False
    nan_mask = (numpy.isnan(values))
    values[numpy.where(nan_mask)] = var_dict['_FillValue']  # avoid warning
    out_of_range_mask = (values > 100.)
    _mask = (nan_mask | out_of_range_mask)
    result: numpy.typing.NDArray = numpy.ma.getdata(_mask)
    return result


def mask_wind(var_dicts: typing.Dict[str, typing.Any],
              var_id: str
              ) -> numpy.typing.NDArray:
    """Build mask for Wind speed.

    Parameters
    ----------
    var_dict: dict
        Dictionary describing the Wind speed variable

    Returns
    -------
    numpy.ndarray
        Array with cells set to True where values should be masked , i.e. NaN
        or aberrant values (absolute values above 200m.s-1).
    """
    var_dict = var_dicts[var_id]
    values = var_dict['array']
    values._sharedmask = False
    nan_mask = (numpy.isnan(values))
    values[numpy.where(nan_mask)] = var_dict['_FillValue']  # avoid warning
    out_of_range_mask = (numpy.absolute(values) > 200.)
    _mask = (nan_mask | out_of_range_mask)
    result: numpy.typing.NDArray = numpy.ma.getdata(_mask)
    return result


def mask_rain(rain: numpy.typing.NDArray
              ) -> numpy.typing.NDArray:
    """Build mask using Rain flag for Wind, SSH and Sigma0.

    Parameters
    ----------
    rain: numpy.ndarray
        Rain flag variable

    Returns
    -------
    numpy.ndarray
        Array with cells set to True where values should be masked , i.e. Rain
        or high probability of rain from altimeter.
    """
    # build rain flag from bits
    RAIN_BITS = {'no_rain': 0,
                 'rain': 1,
                 'high_rain_probability from_altimeter': 2,
                 'high_probabilty_of_no_rain_from_altimeter': 3,
                 'ambiguous': 4}

    b_rain = numpy.int8(0)
    for frain in ('rain', 'high_rain_probability from_altimeter'):
        b_rain = b_rain + (1 << RAIN_BITS[frain])
    result = (numpy.bitwise_and(rain, b_rain) > 0)
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
    variables = {'wind_speed_alt': {'name': 'wind_speed',
                                    'long_name': 'Wind speed',
                                    'units': 'm.s-1',
                                    'valid_min': 0.0,
                                    'valid_max': 25.4,
                                    'options': {}},
                 'ssha': {'name': 'ssha',
                          'long_name': 'Sea surface height anomaly',
                          'units': 'm',
                          'valid_min': -1.0,
                          'valid_max': 1.0,
                          'options': {}},
                 'swh_ocean': {'name': 'swh',
                               'long_name': 'Significant wave height',
                               'units': 'm',
                               'valid_min': 0.0,
                               'valid_max': 25.0,
                               'options': {}},
                 'sig0_ocean': {'name': 'sigma0',
                                'long_name': 'Sigma0',
                                'units': '',
                                'valid_min': 5.0,
                                'valid_max': 30.0,
                                'options': {}}}

    idf_version = output_opts.get('idf_version', '1.0')

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    freq_hz = int(input_opts.get('frequency', 1))
    if freq_hz not in (1, 20):
        raise FrequencyNotSupported(freq_hz)

    lon_name = 'longitude'
    lat_name = 'latitude'
    time_name = 'time'
    surface_name = 'surface_classification_flag'
    mask_methods = {'ssha': mask_ssha,
                    'swh_ocean': mask_swh,
                    'sig0_ocean': mask_sig0,
                    'wind_speed_alt': mask_wind}

    values: typing.Dict[str, numpy.typing.NDArray] = {}
    get_netcdf_values = idf_converter.lib.extract_variable_values

    f_handler = netCDF4.Dataset(input_path, 'r')
    d_group = f'data_{freq_hz:02d}'
    d_handler = f_handler[d_group]
    if 1 == freq_hz:
        spatial_res_meters = 7000  # very approximative
        time = get_netcdf_values(d_handler, time_name)
        lon = get_netcdf_values(d_handler, lon_name)
        lat = get_netcdf_values(d_handler, lat_name)
        surface = get_netcdf_values(d_handler, surface_name)
        rms = get_netcdf_values(d_handler['ku'], 'swh_ocean_rms')
        rain = get_netcdf_values(d_handler, 'rain_flag')
        rain_mask = mask_rain(rain)
    elif 20 == freq_hz:
        _ = variables.pop('wind_speed_alt')
        spatial_res_meters = 350  # very approximative
        time = get_netcdf_values(d_handler['ku'], time_name)
        lon = get_netcdf_values(d_handler['ku'], lon_name)
        lat = get_netcdf_values(d_handler['ku'], lat_name)
        surface = get_netcdf_values(d_handler['ku'], surface_name)

    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables
    for var_id in variables.keys():
        if 'wind' in var_id:
            idf_converter.lib.extract_variable_attributes(d_handler, var_id,
                                                          granule)
            band = get_netcdf_values(d_handler, var_id)
        else:
            idf_converter.lib.extract_variable_attributes(d_handler['ku'],
                                                          var_id,
                                                          granule)
            band = get_netcdf_values(d_handler['ku'], var_id)

        if (('sigma0' in var_id or 'swh' in var_id) and (freq_hz == 1)):
            _name = f'{var_id}_qual'
            mask = get_netcdf_values(d_handler['ku'], _name)
            band[numpy.where(mask == 1)] = numpy.nan

        values[var_id] = band

    idf_converter.lib.extract_global_attributes(f_handler, input_opts,
                                                granule)
    f_handler.close()

    # Trick to deal with continuity in longitude
    lref = lon[int(0.5 * numpy.shape(lon)[0])]
    lon = numpy.mod(lon - (lref - 180.), 360.) + (lref - 180.)
    lon = numpy.rad2deg(numpy.unwrap(numpy.deg2rad(lon)))

    granule.vars['lat'] = {'array': None,
                           'units': 'degrees north',
                           'datatype': lat.dtype,
                           'options': {}}

    granule.vars['lon'] = {'array': None,
                           'units': 'degrees east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Apply time offset to transform time into an EPOCH timestamp
    ref_time = datetime.datetime(2000, 1, 1)
    epoch = datetime.datetime(1970, 1, 1)
    time_offset = (ref_time - epoch).total_seconds()
    shifted_time = (time + time_offset).astype(numpy.double)

    time_units = 'seconds since 1970-01-01T00:00:00.000Z'
    granule.vars['time'] = {'array': None,
                            'units': time_units,
                            'datatype': numpy.double,
                            'options': {}}

    channels = list(values.keys())
    _granule_name = os.path.basename(os.path.dirname(input_path))
    granule_name = f'{_granule_name}_{freq_hz:02d}hz'
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_res_meters
    granule.meta['idf_spatial_resolution_units'] = 'm'

    for var_id, band in values.items():
        granule.vars[var_id]['array'] = band
        granule.vars[var_id]['datatype'] = band.dtype

    granule.vars['lat']['array'] = lat
    granule.vars['lon']['array'] = lon
    granule.vars['time']['array'] = shifted_time

    granule.dims['time'] = numpy.size(granule.vars['time']['array'])

    start_dt = datetime.datetime.utcfromtimestamp(shifted_time[0])
    stop_dt = datetime.datetime.utcfromtimestamp(shifted_time[-1])

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    transforms = []

    surface_mask = (surface > 0)
    transforms.append(('static_common_mask', {'targets': channels,
                                              'mask': surface_mask}))
    if freq_hz == 1:
        rms_mask = (rms > 1)
        transforms.append(('static_common_mask', {'targets': channels,
                                                  'mask': rms_mask}))

        channels_rain = [item for item in channels if 'swh' not in item]
        transforms.append(('static_common_mask', {'targets': channels_rain,
                                                  'mask': rain_mask}))

    transforms.append(('remove_extra_lon_degrees', {'lon_name': 'lon'}))

    transforms.append(('mask_methods', {'targets': channels,
                                        'methods': mask_methods}))

    output_opts['__export'] = channels

    # data_model, dims, vars, attrs, formatter_jobs
    yield (input_opts, output_opts, granule, transforms)
