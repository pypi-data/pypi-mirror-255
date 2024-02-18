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

import numpy
import typing
import logging
import idf_converter.lib
import idf_converter.readers.netcdf_grid_latlon
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger()

DATA_MODEL = idf_converter.readers.netcdf_grid_latlon.DATA_MODEL


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    in_msg, out_msg = idf_converter.readers.netcdf_grid_latlon.help()
    return (in_msg, out_msg)


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

    # Define default input options
    if 'time_variable' not in input_opts:
        input_opts['time_variable'] = 'time'
    if 'lon_variable' not in input_opts:
        input_opts['lon_variable'] = 'longitude'
    if 'lat_variable' not in input_opts:
        input_opts['lat_variable'] = 'latitude'
    if 'variables' not in input_opts:
        input_opts['variables'] = 'VMDR,VHM0,VTM02,VTM10,VTPK,VPED'
        input_opts['variables'] += ',VMDR_WW,VHM0_WW,VTM01_WW'
        input_opts['variables'] += ',VMDR_SW1,VHM0_SW1,VTM01_SW1'
        input_opts['variables'] += ',VMDR_SW2,VHM0_SW2,VTM01_SW2'
        input_opts['variables'] += ',VSDX,VSDY'
    if 'time_coverage_relative_start' not in input_opts:
        input_opts['time_coverage_relative_start'] = '0'
    if 'time_coverage_relative_end' not in input_opts:
        input_opts['time_coverage_relative_end'] = '10800'
    if 'global_overrides' not in input_opts:
        input_opts['global_overrides'] = 'processing_level:L4'
        input_opts['global_overrides'] += ',product_version:1.0'
        input_opts['global_overrides'] += ',file_version:1.0'

    grid_latlon = idf_converter.readers.netcdf_grid_latlon
    for result in grid_latlon.read_data(input_opts, output_opts):
        input_opts, output_opts, granule, _transforms = result

        # The transforms list returned by the lat/lon grid reader is shared by
        # all the subgranules, i.e. modifying this list in a loop has
        # side-effects for the subsequent iterations.
        # Create a brand new transforms list to avoid this problem.
        transforms = []

        directions = [x for x in ('VMDR', 'VMDR_SW1', 'VMDR_SW2', 'VMDR_WW')
                      if x in granule.vars.keys()]
        if 0 < len(directions):
            dir_cfg = {x: {'direction': x,
                           'module': None,
                           'radians': False,
                           'angle_to_east': numpy.pi / 2.0,
                           'clockwise': True,
                           'meteo': True} for x in directions}
            transforms.append(('dir2vectors', {'targets': directions,
                                               'configs': dir_cfg}))

        # Add eastward_ and northward_ variables to the export targets
        targets = output_opts['__export']
        for dir_var_name in directions:
            targets.append(f'eastward_{dir_var_name}')
            targets.append(f'northward_{dir_var_name}')
        output_opts['__export'] = targets

        yield (input_opts, output_opts, granule, transforms)
