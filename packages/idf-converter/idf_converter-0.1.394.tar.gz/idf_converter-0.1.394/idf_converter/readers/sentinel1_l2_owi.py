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
import numpy.typing
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'
INV_QC = {'good': 0, 'medium': 1, 'poor': 2}
WIND_QC = {'good': 0, 'medium': 1, 'low': 2, 'poor': 3}


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('',)
    return ('\n'.join(inp), '\t'.join(out))


def build_mask(f_handler: netCDF4.Dataset,
               granule: Granule
               ) -> numpy.typing.NDArray:
    """"""
    if 'owiLandFlag' in f_handler.variables.keys():
        # IPF version < 2.9
        _land_flag = f_handler.variables['owiLandFlag'][:]
        _inv_quality = f_handler.variables['owiInversionQuality'][:]
        _wind_quality = f_handler.variables['owiWindQuality'][:]
        _no_wind = (granule.vars['owiWindSpeed']['array'] == 0)
        _dir180 = (granule.vars['owiWindDirection']['array'] == 180)
        _mask = ((_land_flag != 0) |
                 (_no_wind & _dir180) |
                 (_no_wind & (_wind_quality == WIND_QC['poor'])) |
                 (_no_wind & (_inv_quality == INV_QC['poor'])))
        old_mask: numpy.typing.NDArray = numpy.ma.getdata(_mask)
        return old_mask

    # IPF version >= 2.9
    _mask = f_handler.variables['owiMask'][:]
    speed_mask = numpy.ma.getmaskarray(granule.vars['owiWindSpeed']['array'])
    dir_mask = numpy.ma.getmaskarray(granule.vars['owiWindDirection']['array'])
    mask: numpy.typing.NDArray = (speed_mask | dir_mask | (_mask != 0))
    return mask


def _get_name_and_time_range(f_handler: netCDF4.Dataset,
                             input_path: str
                             ) -> typing.Tuple[str, str, str]:
    """"""
    _granule_name = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(_granule_name)
    start_str = f_handler.firstMeasurementTime
    stop_str = f_handler.lastMeasurementTime

    # L2 NetCDF filename and first/lastMeasurementTime attributes are not
    # reliable on older versions of the IPF, so acquire the info from the name
    # of the source SAFE instead
    _ipf_version = getattr(f_handler, 'IPFversion', 0.0)
    ipf_version = float(_ipf_version)
    if ipf_version < 3.4:
        source_product = f_handler.sourceProduct
        source_split = source_product.split('_')
        start_str = source_split[6]
        start_dt = datetime.datetime.strptime(start_str, '%Y%m%dT%H%M%S')
        start_str = f'{start_dt:%Y-%m-%dT%H:%M:%SZ}'
        stop_str = source_split[7]
        stop_dt = datetime.datetime.strptime(stop_str, '%Y%m%dT%H%M%S')
        stop_str = f'{stop_dt:%Y-%m-%dT%H:%M:%SZ}'
        unique_str = source_split[-1].split('.')[0]
        granule_name = f'{granule_name}_{unique_str}'

    return granule_name, start_str, stop_str


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
    variables: typing.Dict[str, typing.Dict[str, typing.Any]]
    variables = {'owiWindSpeed': {'name': 'owiWindSpeed',
                                  'options': {}},
                 'owiWindDirection': {'name': 'owiWindDirection',
                                      'options': {}},
                 'owiEcmwfWindSpeed': {'name': 'owiEcmwfWindSpeed',
                                       'options': {}},
                 'owiEcmwfWindDirection': {'name': 'owiEcmwfWindDirection',
                                           'options': {}},
                 'owiRadVel': {'name': 'owiRadVel',
                               'valid_min': -2.5,
                               'valid_max': 2.5,
                               'options': {}}}

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    # Read variables
    f_handler = netCDF4.Dataset(input_path, 'r')
    for var_id in variables.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(_band)
    lon = idf_converter.lib.extract_variable_values(f_handler, 'owiLon')
    lat = idf_converter.lib.extract_variable_values(f_handler, 'owiLat')
    _platform = f_handler.missionName
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    nrow = f_handler.dimensions['owiAzSize'].size
    ncell = f_handler.dimensions['owiRaSize'].size
    mask = build_mask(f_handler, granule)
    granule_name, start_str, stop_str = _get_name_and_time_range(f_handler,
                                                                 input_path)
    f_handler.close()

    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    if '.' in start_str:
        start_dt = datetime.datetime.strptime(start_str,
                                              '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%SZ')

    if '.' in stop_str:
        stop_dt = datetime.datetime.strptime(stop_str,
                                             '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        stop_dt = datetime.datetime.strptime(stop_str, '%Y-%m-%dT%H:%M:%SZ')
    platform = f'Sentinel-1{_platform[-1].upper()}'

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 1000
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = platform
    granule.meta['sensor'] = 'C-SAR'

    # Include the L2 SAFE name as a global attribute if the input file was in
    # a SAFE directory layout
    input_dir = os.path.dirname(input_path)
    parent_name = os.path.basename(input_dir)
    if 'measurement' == parent_name:
        grandparent_name = os.path.basename(os.path.dirname(input_dir))
        if grandparent_name.endswith('.SAFE'):
            granule.meta['L2_SAFE'] = grandparent_name

    # Add transforms
    transforms = []

    dir_cfg = {'wind': {'direction': 'owiWindDirection',
                        'module': 'owiWindSpeed',
                        'radians': False,
                        'meteo': True,
                        'angle_to_east': numpy.pi / 2.0,
                        'clockwise': True},
               'ecmwf': {'direction': 'owiEcmwfWindDirection',
                         'module': 'owiEcmwfWindSpeed',
                         'radians': False,
                         'meteo': True,
                         'angle_to_east': numpy.pi / 2.0,
                         'clockwise': True}}
    transforms.append(('dir2vectors', {'targets': ('wind', 'ecmwf'),
                                       'configs': dir_cfg}))

    channels = ['eastward_wind', 'northward_wind', 'eastward_ecmwf',
                'northward_ecmwf', 'owiRadVel']

    # Remove direction and modulus variables
    to_remove = ('owiWindDirection', 'owiWindSpeed', 'owiEcmwfWindDirection',
                 'owiEcmwfWindSpeed')
    transforms.append(('remove_vars', {'targets': to_remove}))

    # Apply mask for inverted wind
    transforms.append(('static_common_mask', {'targets': ('eastward_wind',
                                                          'northward_wind'),
                                              'mask': mask}))

    output_opts['__export'] = channels

    yield input_opts, output_opts, granule, transforms
