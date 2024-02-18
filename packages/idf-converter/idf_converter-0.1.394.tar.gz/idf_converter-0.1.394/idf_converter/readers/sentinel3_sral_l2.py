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
import defusedxml.ElementTree as ET
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'time_dependent'


class InputPathMissing(ValueError):
    """Error raised when the input options have no "path" entry"""
    pass


class FrequencyNotSupported(ValueError):
    """Error raised when the requested frequency is neither 1Hz not 20Hz, the
    only frequencies available in the input files."""
    def __init__(self, frequency: int) -> None:
        """"""
        self.frequency = frequency
        msg = 'This reader only supports 1Hz and 20Hz data'
        super(FrequencyNotSupported, self).__init__(msg)


class TimelinessNotSupported(Exception):
    """Error raised when the input file corresponds to a Non Time Critical
    product and 20Hz data are requested: the reader only supports 20Hz for
    Near Real Time products."""
    def __init__(self, timeliness: str) -> None:
        """"""
        self.timeliness = timeliness


class NotEnoughData(Exception):
    """Error raised when the input data has less than 3 values, which is the
    minimal values count supported by this reader."""
    def __init__(self) -> None:
        """"""
        msg = 'This reader requires at least three along-track values'
        super(NotEnoughData, self).__init__(msg)


def get_timeliness(input_dir: str) -> typing.Optional[str]:
    """ Read metadata in xml file. Return start and track Offset, number of
    lines and elements spatial resolution for Tie Points, 1 km nadir and 1 km
    oblique grid."""
    manifest_path = os.path.join(input_dir, 'xfdumanifest.xml')
    if not os.path.exists(manifest_path):
        return None
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    s3path = '{http://www.esa.int/safe/sentinel/sentinel-3/1.0}'
    for a_child in root.findall("./*/metadataObject/metadataWrap/xmlData/*"):
        for child in a_child:
            if child.tag == f'{s3path}timeliness':
                return str(child.text)
    return None


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
    variables = {'wind': {'name': 'wind_speed',
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
                 'swh': {'name': 'swh',
                         'long_name': 'Significant wave height',
                         'units': 'm',
                         'valid_min': 0.0,
                         'valid_max': 25.0,
                         'options': {}},
                 'sig0': {'name': 'sigma0',
                          'long_name': 'Sigma0',
                          'units': '',
                          'valid_min': 5.0,
                          'valid_max': 30.0,
                          'options': {}},
                 'tb238': {'name': 'tb_238_01',
                           'long_name': ('23.8Ghz main beam brightness '
                                         'temperature: 1Hz'),
                           'units': 'K',
                           'valid_min': 135.15,
                           'valid_max': 265.15,
                           'options': {}},
                 'tb365': {'name': 'tb_365_01',
                           'long_name': ('36.5Ghz main beam brightness '
                                         'temperature: 1Hz'),
                           'units': 'K',
                           'valid_min': 135.15,
                           'valid_max': 265.15,
                           'options': {}}}

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    freq_hz = int(input_opts.get('frequency', 1))

    if 1 == freq_hz:
        lon_name = 'lon_01'
        lat_name = 'lat_01'
        time_name = 'time_01'
        surface_name = 'surf_type_01'
        spatial_res_meters = 7000  # very approximative
        granule.vars['wind_speed_alt_01_ku'] = granule.vars.pop('wind')
        granule.vars['ssha_01_ku'] = granule.vars.pop('ssha')
        granule.vars['swh_ocean_01_ku'] = granule.vars.pop('swh')
        granule.vars['sig0_ocean_01_ku'] = granule.vars.pop('sig0')
        granule.vars['tb_238_01'] = granule.vars.pop('tb238')
        granule.vars['tb_365_01'] = granule.vars.pop('tb365')
        mask_methods = {'ssha_01_ku': mask_ssha,
                        'swh_ocean_01_ku': mask_swh,
                        'sig0_ocean_01_ku': mask_sig0,
                        'wind_speed_alt_01_ku': mask_wind}
    elif 20 == freq_hz:
        lon_name = 'lon_20_ku'
        lat_name = 'lat_20_ku'
        time_name = 'time_20_ku'
        surface_name = 'surf_type_20_ku'
        spatial_res_meters = 300  # very approximative
        del granule.vars['wind']  # no wind at 20Hz
        del granule.vars['tb238']  # no 23.8GHz brightness temperature at 20Hz
        del granule.vars['tb365']  # no 36.5GHz brightness temperature at 20Hz
        granule.vars['ssha_20_ku'] = granule.vars.pop('ssha')
        granule.vars['swh_ocean_20_ku'] = granule.vars.pop('swh')
        granule.vars['sig0_ocean_20_ku'] = granule.vars.pop('sig0')
        mask_methods = {'ssha_20_ku': mask_ssha,
                        'swh_ocean_20_ku': mask_swh,
                        'sig0_ocean_20_ku': mask_sig0}
    else:
        raise FrequencyNotSupported(freq_hz)

    channels = list(granule.vars.keys())

    f_handler = netCDF4.Dataset(input_path, 'r')
    _time = idf_converter.lib.extract_variable_values(f_handler, time_name)
    _lon = idf_converter.lib.extract_variable_values(f_handler, lon_name)
    _lat = idf_converter.lib.extract_variable_values(f_handler, lat_name)
    for var_id in granule.vars.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = band
        granule.vars[var_id]['datatype'] = band.dtype

    surface = idf_converter.lib.extract_variable_values(f_handler,
                                                        surface_name)
    tb238_quality = None
    if 'tb_238_01' in granule.vars.keys():
        flag_name = 'tb_238_quality_flag_01'
        tb238_quality = idf_converter.lib.extract_variable_values(f_handler,
                                                                  flag_name)
    tb365_quality = None
    if 'tb_365_01' in granule.vars.keys():
        flag_name = 'tb_365_quality_flag_01'
        tb365_quality = idf_converter.lib.extract_variable_values(f_handler,
                                                                  flag_name)

    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    f_handler.close()

    granule.vars['lat'] = {'array': _lat,
                           'units': 'degrees north',
                           'datatype': _lat.dtype,
                           'options': {}}

    # Trick to deal with continuity in longitude
    lref = _lon[int(0.5 * numpy.shape(_lon)[0])]
    _lon = numpy.mod(_lon - (lref - 180.), 360.) + (lref - 180.)
    _lon = numpy.rad2deg(numpy.unwrap(numpy.deg2rad(_lon)))
    granule.vars['lon'] = {'array': _lon,
                           'units': 'degrees east',
                           'datatype': _lon.dtype,
                           'options': {}}

    # Apply time offset to transform time into an EPOCH timestamp
    ref_time = datetime.datetime(2000, 1, 1)
    epoch = datetime.datetime(1970, 1, 1)
    time_offset = (ref_time - epoch).total_seconds()
    shifted_time = _time + time_offset
    granule.vars['time'] = {'array': shifted_time.astype(numpy.double),
                            'units': 'seconds since 1970-01-01T00:00:00.000Z',
                            'datatype': numpy.double,
                            'options': {}}

    granule.dims['time'] = numpy.size(granule.vars['time']['array'])

    start_dt = datetime.datetime.utcfromtimestamp(shifted_time[0])
    stop_dt = datetime.datetime.utcfromtimestamp(shifted_time[-1])
    granule_name = os.path.basename(os.path.dirname(input_path))

    granule.meta['idf_granule_id'] = '{}_{:02d}Hz'.format(granule_name,
                                                          freq_hz)
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_res_meters
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    transforms = []

    transforms.append(('static_common_mask', {'targets': channels,
                                              'mask': (surface > 1)}))

    mwr_channels = [_ for _ in ('tb_238_01', 'tb_365_01',)
                    if _ in granule.vars.keys()]
    if 0 < len(mwr_channels):
        bands_mask = {'tb_238_01': (tb238_quality != 0),
                      'tb_365_01': (tb365_quality != 0)}
        transforms.append(('static_bands_mask', {'targets': mwr_channels,
                                                 'masks': bands_mask
                                                 }))
    else:
        logger.debug('No MWR variable')

    transforms.append(('remove_extra_lon_degrees', {'lon_name': 'lon'}))

    _channels = [_ for _ in channels if _ not in mwr_channels]
    transforms.append(('mask_methods', {'targets': _channels,
                                        'methods': mask_methods}))

    output_opts['__export'] = channels

    # data_model, dims, vars, attrs, formatter_jobs
    yield (input_opts, output_opts, granule, transforms)
