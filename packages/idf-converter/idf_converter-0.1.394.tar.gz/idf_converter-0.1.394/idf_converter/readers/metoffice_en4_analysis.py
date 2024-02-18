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
import typing
import netCDF4
import logging
import idf_converter.lib
import idf_converter.lib.time
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = idf_converter.readers.netcdf_grid_latlon.DATA_MODEL


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

    # Read variables
    f_handler = netCDF4.Dataset(input_path, 'r')
    t_units = f_handler.variables['time'].units
    t_bounds = f_handler.variables['time_bnds'][0, :]
    f_handler.close()

    dtimes = netCDF4.num2date(t_bounds, t_units)
    dtimes = idf_converter.lib.time.as_datetimes_array(dtimes)
    start_dt = dtimes[0]
    stop_dt = dtimes[-1]

    if 'lon_variable' not in input_opts:
        input_opts['lon_variable'] = 'lon'

    if 'lat_variable' not in input_opts:
        input_opts['lat_variable'] = 'lat'

    if 'depth_variable' not in input_opts:
        input_opts['depth_variable'] = 'depth'

    if 'depth_dimension' not in input_opts:
        input_opts['depth_dimension'] = 'depth'

    if 'variables' not in input_opts:
        input_opts['variables'] = 'temperature,salinity'

    start_str = f'time_coverage_start:"{start_dt:%Y-%m-%dT%H:%M:%SZ}"'
    stop_str = f'time_coverage_end:"{stop_dt:%Y-%m-%dT%H:%M:%SZ}"'
    _global_overrides = input_opts.get('global_overrides', None)
    overrides = ','.join([x for x in (start_str, stop_str, _global_overrides)
                         if x is not None])
    input_opts['global_overrides'] = overrides

    generic = idf_converter.readers.netcdf_grid_latlon.read_data(input_opts,
                                                                 output_opts)
    input_opts, output_opts, granule, transforms = next(generic)

    yield input_opts, output_opts, granule, transforms
