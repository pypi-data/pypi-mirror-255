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
import struct
import typing
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'GRID_LATLON'


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
    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    # Read variables
    with open(input_path, 'rb') as f:
        file_content = f.read()

    fmt = '<{}f'.format(1440*480*8)
    _all_data = struct.unpack(fmt, file_content)
    all_data = numpy.reshape(_all_data, (8, 480, 1440,))
    all_data = numpy.roll(all_data, 720, axis=2)

    granule_fname = os.path.basename(input_path)
    _granule_name = granule_fname  # decompressed binary data have no extension
    _, granule_date = _granule_name.rsplit('_', 1)  # %Y%m%d
    _, version, process, _ = _granule_name.split('_', 3)

    input_opts['geoloc_at_pixel_center'] = 'no'
    dim1 = numpy.array([-60.0 + i * 0.25 for i in range(0, 480)])
    dim2 = numpy.array([-180.0 + i * 0.25 for i in range(0, 1440)])

    granule.vars['lat'] = {'array': dim1,
                           'units': 'degrees_north',
                           'datatype': dim1.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': dim2,
                           'units': 'degrees_east',
                           'datatype': dim2.dtype,
                           'options': {}}

    granule.dims['lat'] = dim1.size
    granule.dims['lon'] = dim2.size

    granule.vars['rain'] = {'name': 'rain',
                            'valid_min': 0.0,
                            'valid_max': 75,
                            'options': {}}

    granule.meta['idf_spatial_resolution'] = 27500  # ~ 1/4 degree
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['institution'] = 'NOAA CPC'

    dtime_base = datetime.datetime.strptime(granule_date, '%Y%m%d')
    for i in range(0, 8):
        hour = 3 * i
        granule_name = '{}_{:02d}'.format(_granule_name, hour)

        start_dt = dtime_base + datetime.timedelta(hours=hour)
        stop_dt = start_dt + datetime.timedelta(hours=3)

        granule.meta['idf_granule_id'] = granule_name
        granule.meta['time_coverage_start'] = start_dt
        granule.meta['time_coverage_end'] = stop_dt

        # input contains 3-hourly rate, we want the amount of precipitation
        # during these 3 hours
        _data = all_data[i, :, :] * 3
        granule.vars['rain']['array'] = _data

        transforms = []

        # Mask where there are no precipitations
        mask = (_data <= 0.0)  # nodata is -999
        transforms.append(('static_common_mask', {'targets': ('rain',),
                                                  'mask': mask}))

        output_opts['__export'] = ['rain', ]

        yield input_opts, output_opts, granule, transforms
