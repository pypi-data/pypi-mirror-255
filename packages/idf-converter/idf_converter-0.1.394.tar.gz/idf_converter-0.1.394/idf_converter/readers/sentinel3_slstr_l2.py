# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-27
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
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger(__name__)

MasksDict = typing.Dict[str, numpy.typing.NDArray]
DATA_MODEL = 'SWATH'
MAX_DIM_SIZE = 2**13

# https://earth.esa.int/web/sentinel/technical-guides/sentinel-3-slstr/level-1/vis-and-swir-radiances
# https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-slstr/data-formats/level-1
# https://earth.esa.int/web/sentinel/user-guides/sentinel-3-slstr/product-types/level-1b
# https://sentinel.esa.int/documents/247904/685236/Sentinel-3_User_Handbook#%5B%7B%22num%22%3A235%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C54%2C628%2C0%5D
# S1 555   nm            B
# S2 659   nm            G
# S3 865   nm            R
# S4 1.375 microm
# S5 1.610 microm
# S6 2.25  microm
# S7 3.74  microm        IR
# S8 10.85 microm        IR
# S9 12    microm        IR


class InputPathMissing(IOError):
    """"""
    pass


class TimelinessNotSupported(Exception):
    """Error raised when the input file is a Non Time Critical product: this
    reader only supports Near Real Time products."""
    def __init__(self, timeliness: str) -> None:
        """"""
        self.timeliness = timeliness


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


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

    variables = {'sea_surface_temperature': {'name': 'sea_surface_temperature',
                                             'valid_min': 270.150,
                                             'valid_max': 310.150,
                                             'options': {}},
                 'wind_speed': {'name': 'wind_speed',
                                'long_name': 'wind speed',
                                'valid_min': 0.000,
                                'valid_max': 25.400,
                                'options': {}}}

    channels = list(variables.keys())

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    input_dir = os.path.dirname(input_path)
    timeliness = get_timeliness(input_dir)
    logger.debug(f'timeliness: {timeliness}')
    if timeliness is None:
        logger.warning('Could not read data timeliness. Please note that only '
                       'NRT data are supported')
    elif 'NT' == timeliness:
        logger.error('Input data are not supported due to the size of the '
                     'along-track dimension which exceeds SEAScope '
                     'capabilities')
        raise TimelinessNotSupported(timeliness)

    f_handler = netCDF4.Dataset(input_path, 'r')
    for var_id in channels:
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        band = _band[0, :, :]
        granule.vars[var_id]['array'] = numpy.ma.array(band)
    lon = idf_converter.lib.extract_variable_values(f_handler, 'lon')
    lat = idf_converter.lib.extract_variable_values(f_handler, 'lat')
    _sst_dtime = idf_converter.lib.extract_variable_values(f_handler,
                                                           'sst_dtime')
    sst_dtime = _sst_dtime[0, :, :]
    _time = idf_converter.lib.extract_variable_values(f_handler, 'time')
    time0 = _time[0]
    time0_units = f_handler.variables['time'].units
    _ql = idf_converter.lib.extract_variable_values(f_handler,
                                                    'quality_level')
    ql = _ql[0, :, :]
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    f_handler.close()

    dtime0 = netCDF4.num2date(time0, units=time0_units)

    nrow, ncell = numpy.shape(granule.vars['sea_surface_temperature']['array'])
    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    # Handle longitude continuity
    dlon = lon[1:, :] - lon[:-1, :]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon[numpy.where(lon < 0.0)] = lon[numpy.where(lon < 0.0)] + 360.0

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = dtime0 + datetime.timedelta(seconds=numpy.min(sst_dtime))
    stop_dt = dtime0 + datetime.timedelta(seconds=numpy.max(sst_dtime))

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 1000  # 1km
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'Eumetsat'
    granule.meta['platform'] = 'Sentinel-3'
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'SLSTR'
    granule.meta['sensor_type'] = 'dual scan temperature radiometer'

    # Add transforms
    transforms = []

    # Mask where quality is subpar
    ql_mask = numpy.full(numpy.shape(ql), True, dtype='bool')
    ql_mask[numpy.where(ql > 2)] = False
    transforms.append(('static_common_mask', {'targets': channels.copy(),
                                              'mask': ql_mask}))

    output_opts['__export'] = channels

    yield (input_opts, output_opts, granule, transforms)
