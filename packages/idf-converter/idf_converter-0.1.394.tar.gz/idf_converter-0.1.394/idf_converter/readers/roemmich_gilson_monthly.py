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
import idf_converter.lib
import dateutil.relativedelta
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
    t = f_handler.variables['TIME'][:]
    f_handler.close()

    base_dt = datetime.datetime(2004, 1, 15, 12, 0, 0)
    _dtimes = [base_dt + dateutil.relativedelta.relativedelta(months=x)
               for x in numpy.floor(t).astype('int')]
    dtimes = numpy.array(_dtimes)

    input_opts['time_variable'] = 'TIME'
    input_opts['lon_variable'] = 'LONGITUDE'
    input_opts['lat_variable'] = 'LATITUDE'
    input_opts['depth_variable'] = 'PRESSURE'
    input_opts['depth_dimension'] = 'PRESSURE'
    input_opts['time_units'] = 'seconds since 1980-01-01'
    input_opts['time_coverage_relative_start'] = 'month_beginning'
    input_opts['time_coverage_relative_end'] = 'month_end'
    input_opts['indicative_times'] = dtimes

    generic = idf_converter.readers.netcdf_grid_latlon.read_data(input_opts,
                                                                 output_opts)
    for input_opts, output_opts, granule, transforms in generic:
        yield input_opts, output_opts, granule, transforms
