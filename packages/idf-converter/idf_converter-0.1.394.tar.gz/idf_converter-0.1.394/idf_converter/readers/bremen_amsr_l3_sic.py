# vim: ts=4:sts=4:sw=4
#
# @date 2019-10-10
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
import pyproj
import netCDF4
import logging
import datetime
import idf_converter.lib
import idf_converter.readers.netcdf_grid_yx
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger()

DATA_MODEL = idf_converter.readers.netcdf_grid_yx.DATA_MODEL


class FilenamePatternNotSupported(ValueError):
    """Error raised when the name of the input file does nt match any known
    pattern, preventing the detecting of the time coverage, platform and
    sensor."""
    def __init__(self, file_name: str) -> None:
        """"""
        self.file_name = file_name


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    in_msg, out_msg = idf_converter.readers.netcdf_grid_yx.help()
    return (in_msg, out_msg)


def mask_where_no_ice(var_dicts: typing.Dict[str, typing.Any],
                      var_id: str) -> numpy.typing.NDArray:
    """Build mask for ice concentration.

    Parameters
    ----------
    var_dict: dict
        Dictionary describing the sea ice concentration variable

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
    values[numpy.where(nan_mask)] = -1.0
    zero_mask = (values <= 0.0)
    _mask = (nan_mask | zero_mask)
    mask: numpy.typing.NDArray = numpy.ma.getdata(_mask)
    return mask


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
        raise idf_converter.readers.netcdf_grid_yx.InputPathMissing()
    input_path = os.path.normpath(_input_path)

    logger.warning('Guessing granule time coverage from the input file '
                   'name is not a good practice: it is only used here '
                   'because time coverage information is missing from the '
                   'netCDF content.')
    file_name = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(file_name)
    name_elements = granule_name.split('-')
    start_dt = None
    platform = None
    sensor = None
    if 4 == len(name_elements):
        start_dt = datetime.datetime.strptime(name_elements[2], '%Y%m%d')
        platform = 'Aqua'
        sensor = 'AMSR-E'
    elif 5 == len(name_elements):
        start_dt = datetime.datetime.strptime(name_elements[3], '%Y%m%d')
        platform = 'GCOM-W1'
        sensor = 'AMSR-2'
    else:
        raise FilenamePatternNotSupported(file_name)

    stop_dt = start_dt + datetime.timedelta(seconds=86400)

    start_str = f'{start_dt:%Y-%m-%dT%H:%M:%SZ}'
    stop_str = f'{stop_dt:%Y-%m-%dT%H:%M:%SZ}'
    if 'global_overrides' in input_opts:
        input_opts['global_overrides'] += f',time_coverage_start:"{start_str}"'
        input_opts['global_overrides'] += f',time_coverage_end:"{stop_str}"'
    else:
        input_opts['global_overrides'] = f'time_coverage_start:"{start_str}"'
        input_opts['global_overrides'] += f',time_coverage_end:"{stop_str}"'

    if 'x_variable' not in input_opts:
        input_opts['x_variable'] = 'x'
    if 'y_variable' not in input_opts:
        input_opts['y_variable'] = 'y'
    if 'variables' not in input_opts:
        input_opts['variables'] = 'z'
    if 'spatial_resolution' not in input_opts:
        input_opts['spatial_resolution'] = 6250
    if 'projection' not in input_opts:
        f_handler = netCDF4.Dataset(input_path, 'r')
        _crs = f_handler.variables['polar_stereographic']
        crs = pyproj.CRS.from_cf({x: getattr(_crs, x) for x in _crs.ncattrs()})
        input_opts['projection'] = crs.to_wkt()
        f_handler.close()

    grid_yx = idf_converter.readers.netcdf_grid_yx
    for result in grid_yx.read_data(input_opts, output_opts):
        input_opts, output_opts, granule, transforms = result

        granule.meta['platform'] = platform
        granule.meta['sensor'] = sensor

        # add mask where there is no ice
        mask_methods = {'z': mask_where_no_ice}
        transforms.insert(0, ('mask_methods', {'targets': ('z',),
                                               'methods': mask_methods}))
        yield (input_opts, output_opts, granule, transforms)
