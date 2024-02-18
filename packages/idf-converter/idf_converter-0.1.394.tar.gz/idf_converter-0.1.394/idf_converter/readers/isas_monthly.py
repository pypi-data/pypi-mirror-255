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
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
import dateutil.relativedelta
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'


class InputPathMissing(IOError):
    """"""
    pass


class DepthValueMissing(Exception):
    """"""
    pass


class DepthValueNotFound(ValueError):
    """"""
    def __init__(self, value: float) -> None:
        """"""
        self.value = value


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

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    _depth_value = input_opts.get('depth_value', None)
    if _depth_value is None:
        raise DepthValueMissing()
    depth_value = float(_depth_value)

    variables = {'PSAL': {'name': 'salinity',
                          'valid_min': 0.0,
                          'valid_max': 40.0,
                          'options': {}},
                 'TEMP': {'name': 'temperature',
                          'valid_min': -2.10,
                          'valid_max': 36.0,
                          'options': {}}}
    granule.vars = variables

    f_handler = netCDF4.Dataset(input_path, 'r')
    try:
        depth_ind = f_handler.variables['depth'][:].tolist().index(depth_value)
    except ValueError:
        logger.error(f'{depth_value}m not found in the values of the depth '
                     'variable')
        depth_ind = -1

    if 0 > depth_ind:
        raise DepthValueNotFound(depth_value)

    to_remove = []
    channels = []
    for var_id in variables:
        if var_id not in f_handler.variables.keys():
            to_remove.append(var_id)
            continue
        else:
            channels.append(var_id)
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        data_slices = (slice(0, 1, None),
                       slice(depth_ind, depth_ind + 1, None),
                       slice(None, None, None), slice(None, None, None))
        granule.vars[var_id]['array'] = numpy.ma.array(_band[data_slices])

    for var_id in to_remove:
        del granule.vars[var_id]

    _lon = idf_converter.lib.extract_variable_values(f_handler, 'longitude')
    _lat = idf_converter.lib.extract_variable_values(f_handler, 'latitude')
    _time = idf_converter.lib.extract_variable_values(f_handler, 'time')
    time_units = f_handler.variables['time'].units
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    f_handler.close()

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 55000  # 0.5°
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['idf_granule_id'] = f'{depth_value}m_{granule_name}'
    granule.dims['row'] = _lat.size
    granule.dims['cell'] = _lon.size

    # Format spatial information
    lat = numpy.tile(_lat[:, numpy.newaxis], (1, _lon.size))
    lon = numpy.tile(_lon[numpy.newaxis, :], (_lat.size, 1))
    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    time_units = time_units.replace('19500101T000000Z', '1950-01-01T00:00:00Z')
    mid_t = netCDF4.num2date(_time[0], time_units)
    start_dt = datetime.datetime(mid_t.year, mid_t.month, 1)
    stop_dt = start_dt + dateutil.relativedelta.relativedelta(months=1)
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    output_opts['gcp_row_spacing'] = 1
    output_opts['gcp_cell_spacing'] = 2

    # Add transforms
    transforms: TransformsList = []

    output_opts['__export'] = channels

    yield (input_opts, output_opts, granule, transforms)
