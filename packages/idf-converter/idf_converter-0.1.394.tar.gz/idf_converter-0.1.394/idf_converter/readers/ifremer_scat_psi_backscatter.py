# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-16
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
import idf_converter.lib
import idf_converter.readers.netcdf_grid_yx
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger()

DATA_MODEL = idf_converter.readers.netcdf_grid_yx.DATA_MODEL
ValuesAndMasks = typing.Tuple[typing.Dict[str, numpy.typing.NDArray],
                              typing.Dict[str, numpy.typing.NDArray]]


class PlatformMissing(Exception):
    """Error raised when neither the "platform" nor the "platform_id" global
    attributes are available in the input file, preventing the identification
    of the platform (necessary to extract the correct variables and apply the
    adquate masking policy)."""
    pass


class PlatformNotSupported(ValueError):
    """Error raised when the platform referenced in the input file is neither
    QuikSCAT nor one of the MetOp satellites, so the variables to extract are
    unknown, as is the masking policy to apply."""
    def __init__(self, platform: str) -> None:
        """"""
        self.platform = platform


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    in_msg, out_msg = idf_converter.readers.netcdf_grid_yx.help()
    return (in_msg, out_msg)


def get_quikscat_mask(ubytes: numpy.typing.NDArray
                      ) -> numpy.typing.NDArray:
    """"""
    mask: numpy.typing.NDArray = ((ubytes == 0) | (ubytes >= 254))

    return mask


def get_metop_mask(ubytes: numpy.typing.NDArray
                   ) -> numpy.typing.NDArray:
    """"""
    mask: numpy.typing.NDArray = ((ubytes == 0) | (ubytes == 255))

    return mask


def _identify_hemisphere(f_handler: netCDF4.Dataset) -> typing.Tuple[str, str]:
    """"""
    # For some reason the latitude variable is entirely msked by default...
    f_handler.variables['latitude'].set_auto_mask(False)
    mean_lat = numpy.mean(f_handler.variables['latitude'][:])

    # The input files contain either the Arctic or the Antarctic region
    if 0.0 < mean_lat:
        projection = 'epsg:3411'
        pole = 'arctic'
    else:
        projection = 'epsg:3412'
        pole = 'antarctic'

    return pole, projection


def _identify_platforms(f_handler: netCDF4.Dataset
                        ) -> typing.Tuple[str, str, typing.List[str]]:
    """"""
    global_attrs = f_handler.ncattrs()
    _platform = None
    if 'platform' in global_attrs:
        _platform = f_handler.platform
    elif 'platform_id' in global_attrs:
        _platform = f_handler.platform_id
    else:
        raise PlatformMissing()

    platform = ''
    sensor = ''
    variables = []
    if 'quikscat' in _platform.lower():
        platform = 'QuikSCAT'
        sensor = 'SeaWinds'
        variables = ['sigma0_mask_inner', 'sigma0_mask_outer']
    elif 'metop' in _platform.lower():
        platforms = []
        if 'b' in _platform.lower():
            platforms.append('MetOp-B')
        else:
            # sometimes MetOp-A is clearly stated, sometimes it is just "MetOp"
            platforms.append('MetOp-A')

        platform = ','.join(platforms)
        sensor = ','.join(['ASCAT'] * len(platforms))
        variables = ['sigma_40_mask', ]
    else:
        raise PlatformNotSupported(_platform)

    return platform, sensor, variables


def _get_values_and_masks(f_handler: netCDF4.Dataset,
                          variables: typing.List[str],
                          platform: str) -> ValuesAndMasks:
    """"""
    # Sigma values have been computed as unsigned bytes with a scale factor and
    # an offset, but have been stored as *signed* bytes without modifying the
    # offset: the upper half of the values range has therefore been shifted to
    # negative values and netCDF4 has no way to guess how these values should
    # be read.
    # The workaround implemented here consists in reading values as unsigned
    # bytes (regardless of what the input file says) before calling the generic
    # grid reader, unpack them correctly and then overwrite the values
    # extracted automatically by the reader.
    values = {}
    masks = {}
    for var_id in variables:
        f_handler.variables[var_id].set_auto_scale(False)
        ubyte_values = f_handler.variables[var_id][:].astype('ubyte')
        f_handler.variables[var_id].set_auto_scale(True)
        if 'QuikSCAT' == platform:
            masks[var_id] = get_quikscat_mask(ubyte_values)
        else:
            masks[var_id] = get_metop_mask(ubyte_values)
        scale = f_handler.variables[var_id].scale_factor
        offset = f_handler.variables[var_id].add_offset
        values[var_id] = numpy.ma.array(offset + scale * ubyte_values)

    return values, masks


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

    f_handler = netCDF4.Dataset(input_path, 'r')

    # Detect which hemisphere is contained in the input file
    pole, projection = _identify_hemisphere(f_handler)

    try:
        # Identify the platform(s) and instrument(s) involved in the creation
        # of the input file
        platform, sensor, variables = _identify_platforms(f_handler)

        # Extract sigma values and masks in advance to bypass formatting quirks
        # in the input files
        values, masks = _get_values_and_masks(f_handler, variables, platform)
    finally:
        f_handler.close()

    input_opts['time_variable'] = 'time'
    input_opts['lat_variable'] = 'latitude'
    input_opts['lon_variable'] = 'longitude'
    input_opts['lat_dimension'] = 'nj'
    input_opts['lon_dimension'] = 'ni'
    input_opts['variables'] = ','.join(variables)
    input_opts['time_coverage_relative_start'] = '-43200'
    input_opts['time_coverage_relative_end'] = '43200'
    input_opts['spatial_resolution'] = 12500
    input_opts['projection'] = projection

    output_opts['use_mean_dydx'] = 'true'

    grid_yx = idf_converter.readers.netcdf_grid_yx
    result = grid_yx.read_data(input_opts, output_opts)
    input_opts, output_opts, granule, transforms = next(result)

    granule.meta['platform'] = platform
    granule.meta['sensor'] = sensor

    # For L4 (merged MetOp-A and MetOp-B), the files for Arctic and Antarctic
    # have the exact same name, so they would get the same granule identifier
    # despite being diffrent IDF files. Prefix with the name of the pole to
    # avoid this issue
    granule.meta['idf_granule_id'] = f'{pole}_{granule.meta["idf_granule_id"]}'

    # Overwrite arrays of sigma values since the netcdf_grid_yx reader could
    # not extract the correct values
    for var_id, var_array in values.items():
        granule.vars[var_id]['array'] = var_array

    # Add mask where there is no ice
    for target, mask in masks.items():
        transforms.insert(0, ('static_common_mask', {'targets': (target,),
                                                     'mask': mask}))

    yield (input_opts, output_opts, granule, transforms)
