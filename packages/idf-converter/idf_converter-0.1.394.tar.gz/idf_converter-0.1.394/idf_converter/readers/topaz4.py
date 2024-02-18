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
import idf_converter.lib
import idf_converter.readers.netcdf_grid_yx
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import ReaderResult

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


def get_ice_mask(granule: Granule
                 ) -> numpy.typing.NDArray:
    """"""
    threshold = 0.00001  # 0.001%
    mask: numpy.typing.NDArray
    mask = (threshold >= numpy.ma.getdata(granule.vars['fice']['array']))
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

    if 'time_variable' not in input_opts:
        input_opts['time_variable'] = 'time'
    if 'x_variable' not in input_opts:
        input_opts['x_variable'] = 'x'
    if 'y_variable' not in input_opts:
        input_opts['y_variable'] = 'y'
    if ('depth_value' in input_opts) and ('depth_variable' not in input_opts):
        input_opts['depth_variable'] = 'depth'
    if ('depth_value' in input_opts) and ('depth_dimension' not in input_opts):
        input_opts['depth_dimension'] = 'depth'
    if 'variables' not in input_opts:
        input_opts['variables'] = 'temperature,salinity,u,v'
    if 'spatial_resolution' not in input_opts:
        input_opts['spatial_resolution'] = 12500
    if 'projection' not in input_opts:
        f_handler = netCDF4.Dataset(input_path, 'r')
        _crs = f_handler.variables['stereographic']
        crs = pyproj.CRS.from_cf({x: getattr(_crs, x) for x in _crs.ncattrs()})
        input_opts['projection'] = crs.to_wkt()
        f_handler.close()

    coords_converted = False
    grid_yx = idf_converter.readers.netcdf_grid_yx
    for result in grid_yx.read_data(input_opts, output_opts):
        input_opts, output_opts, granule, _transforms = result

        if not coords_converted:
            # x and y are provided as multiple of 100km, convert to meters...
            granule.vars['x']['array'] *= 100000
            granule.vars['y']['array'] *= 100000
            coords_converted = True

        if 'fice' in granule.vars.keys():
            transforms = []
            ice_mask = get_ice_mask(granule)

            ice_vars = [_ for _ in ('fice', 'hice', 'uice', 'vice')
                        if _ in granule.vars.keys()]
            mask_job = ('static_common_mask', {'targets': ice_vars,
                                               'mask': ice_mask})
            transforms.append(mask_job)

            transforms.extend(_transforms)
        else:
            transforms = _transforms

        yield (input_opts, output_opts, granule, transforms)
