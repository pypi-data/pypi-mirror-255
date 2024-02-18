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
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'


class InputPathMissing(IOError):
    """"""
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

    variables = ('wind_speed', 'wind_dir', 'model_speed', 'model_dir')
    values = {}
    f_handler = netCDF4.Dataset(input_path, 'r')
    for var_id in variables:
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        values[var_id] = numpy.ma.array(_band)
    lon = idf_converter.lib.extract_variable_values(f_handler, 'lon')
    lat = idf_converter.lib.extract_variable_values(f_handler, 'lat')
    _time = idf_converter.lib.extract_variable_values(f_handler, 'time')
    time_units = f_handler.variables['time'].units
    platform, sensor = f_handler.source.split(' ')
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    nrow = f_handler.dimensions['NUMROWS'].size
    ncell = f_handler.dimensions['NUMCELLS'].size
    f_handler.close()

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 12500
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['platform'] = platform
    granule.meta['sensor'] = sensor

    half_cells = numpy.floor(ncell / 2).astype('int')
    sides = {'left': slice(0, half_cells, None),
             'right': slice(half_cells, None, None)}
    for side, cell_slice in sides.items():
        granule.meta['idf_granule_id'] = f'{granule_name}_{side}'

        granule.dims['row'] = int(nrow)
        granule.dims['cell'] = int(half_cells)
        slices = (slice(None, None, None), cell_slice)

        # Format spatial information
        granule.vars['lat'] = {'array': lat[slices],
                               'units': 'degrees_north',
                               'datatype': lat.dtype,
                               'options': {}}
        granule.vars['lon'] = {'array': lon[slices],
                               'units': 'degrees_east',
                               'datatype': lon.dtype,
                               'options': {}}

        # Format time information
        time_min = _time[slices].min()
        time_max = _time[slices].max()
        start_dt = netCDF4.num2date(time_min, units=time_units)
        stop_dt = netCDF4.num2date(time_max, units=time_units)
        granule.meta['time_coverage_start'] = start_dt
        granule.meta['time_coverage_end'] = stop_dt

        for var_id in values:
            granule.vars[var_id] = {'array': values[var_id][slices]}

        # Add transforms
        transforms = []

        dir_cfg = {'wind': {'direction': 'wind_dir',
                            'module': 'wind_speed',
                            'radians': False,
                            'meteo': False,
                            'angle_to_east': numpy.pi / 2.0,
                            'clockwise': True},
                   'ecmwf': {'direction': 'model_dir',
                             'module': 'model_speed',
                             'radians': False,
                             'meteo': False,
                             'angle_to_east': numpy.pi / 2.0,
                             'clockwise': True}}
        transforms.append(('dir2vectors', {'targets': ('wind', 'ecmwf'),
                                           'configs': dir_cfg}))
        channels = ['eastward_wind', 'northward_wind', 'eastward_ecmwf',
                    'northward_ecmwf']

        # Remove direction and modulus variables
        to_remove = ('wind_dir', 'wind_speed', 'model_dir', 'model_speed')
        transforms.append(('remove_vars', {'targets': to_remove}))

        output_opts['__export'] = channels

        yield (input_opts, output_opts, granule, transforms)
