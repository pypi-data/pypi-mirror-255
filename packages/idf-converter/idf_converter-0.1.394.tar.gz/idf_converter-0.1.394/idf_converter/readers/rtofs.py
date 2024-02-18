# vim: ts=4:sts=4:sw=4
#
# @date 2021-08-13
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
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'


class InputPathMissing(IOError):
    """"""
    pass


class MissingVariablesList(Exception):
    """Error raised when the "variables" input option has not been specified
    by the user."""
    pass


class VariableNotFound(Exception):
    """Error raised when a requested variable is not available in the source
    file."""

    def __init__(self, var_id: str) -> None:
        """"""
        self.var_id = var_id


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

    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        raise MissingVariablesList()
    var_ids = [x.strip() for x in _var_ids.split(',')]

    f_handler = netCDF4.Dataset(input_path, 'r')
    channels = []
    for var_id in var_ids:
        if var_id not in f_handler.variables.keys():
            raise VariableNotFound(var_id)
        else:
            channels.append(var_id)
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        _data_slices = [slice(0, 1, None),  # time
                        slice(None, None, None), slice(None, None, None)]
        if 'Layer' in f_handler.variables[var_id].dimensions:
            _data_slices = [slice(0, 1, None),  # time
                            slice(0, 1, None),  # depth
                            slice(None, None, None), slice(None, None, None)]
        data_slices = tuple(_data_slices)
        granule.vars[var_id]['array'] = numpy.ma.array(_band[data_slices])

        # Compute min/max
        band = granule.vars[var_id]['array']
        band_mask = numpy.ma.getmaskarray(band)
        if band_mask.all():
            granule.vars[var_id]['valid_min'] = 0.0
            granule.vars[var_id]['valid_max'] = 1.0
        else:
            finite_ind = numpy.where(numpy.isfinite(band))
            granule.vars[var_id]['valid_min'] = numpy.min(band[finite_ind])
            granule.vars[var_id]['valid_max'] = numpy.max(band[finite_ind])

    lon = idf_converter.lib.extract_variable_values(f_handler, 'Longitude')
    lat = idf_converter.lib.extract_variable_values(f_handler, 'Latitude')
    _time = idf_converter.lib.extract_variable_values(f_handler, 'MT')
    time_units = f_handler.variables['MT'].units
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    f_handler.close()

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    dt = netCDF4.num2date(_time[0], time_units)

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 9258  # 1/12°
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['idf_granule_id'] = f'{granule_name}_{dt:%Y%m%d%H%M%S}'
    granule.dims['row'] = lat.shape[0]
    granule.dims['cell'] = lon.shape[1]

    # Format spatial information
    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = netCDF4.num2date(_time[0], time_units)
    stop_dt = start_dt + datetime.timedelta(hours=1)
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    # Add transforms
    transforms: TransformsList = []

    output_opts['__export'] = channels

    yield (input_opts, output_opts, granule, transforms)
