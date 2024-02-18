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
import datetime
import idf_converter.lib
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
    title = f_handler.Title
    f_handler.close()

    _, _, _, month_str, _, _ = title.split(' ')
    year = int(month_str[:-3])
    month = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP',
             'OCT', 'NOV', 'DEC'].index(month_str[-3:]) + 1
    indicative_dt = datetime.datetime(year, month, 15, 12, 0, 0)

    input_opts['lon_variable'] = 'LONGITUDE'
    input_opts['lat_variable'] = 'LATITUDE'
    input_opts['depth_variable'] = 'PRES'
    input_opts['depth_dimension'] = 'PRES'
    input_opts['variables'] = 'TOI,SOI'
    input_opts['time_coverage_relative_start'] = 'month_beginning'
    input_opts['time_coverage_relative_end'] = 'month_end'
    input_opts['indicative_time'] = f'{indicative_dt:%Y-%m-%dT%H:%M:%SZ}'

    generic = idf_converter.readers.netcdf_grid_latlon.read_data(input_opts,
                                                                 output_opts)
    input_opts, output_opts, granule, transforms = next(generic)

    yield input_opts, output_opts, granule, transforms
