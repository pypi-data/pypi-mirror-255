# vim: ts=4:sts=4:sw=4
#
# @date 2022-02-24
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
import gzip
import json
import numpy
import typing
import logging
import datetime
import operator
import functools
import numpy.typing
import idf_converter.lib
from pkg_resources import resource_filename
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.readers.remss_l3_wind_netcdf import parse_wind_vars
from idf_converter.readers.remss_l3_wind_netcdf import split_swaths
from idf_converter.readers.remss_l3_wind_netcdf import create_granule
from idf_converter.readers.remss_l3_wind_netcdf import get_wind_transforms

logger = logging.getLogger(__name__)

DATA_MODEL = idf_converter.readers.netcdf_grid_latlon.DATA_MODEL
MutableIndexSlices = typing.List[typing.Union[int, slice]]
IndexSlices = typing.Sequence[typing.Union[int, slice]]
SPEED_VARS = ('WSPD', 'WSPD_LF', 'WSPD_MF', 'WSPD_AW')

"""
Filename prefixes according to REMSS naming convention:

f08: SSMI
f10: SSMI
f11: SSMI
f12: TMI
f13: SSMI
f14: SSMI
f15: SSMI
f16: SSMI
f17: SSMI
f18: SSMI
f32: AMSR-E
f33: AMSR-J
f34: AMSR-2
f35: GMI

qscat: QuikScat
ascat: MetOp-A
ascatb: MetOp-B
ascatc: MetOp-C
"": SeaWinds
wsat: WindSat
"""


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


class MissionMissing(Exception):
    """Error raised when the 'mission' input option has not been specified by
    the user."""
    pass


class TimeUnitsNotSupported(Exception):
    """Error raised when the units of the time variable are not support by this
    reader."""
    def __init__(self, time_units: str) -> None:
        self.time_units = time_units


class InvalidWindVariable(ValueError):
    """Error raised when the value passed to the wind_variables option does not
    match the expected pattern."""
    def __init__(self, value: str) -> None:
        self.wind_variables_str = value


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('    split-swaths\tSet to yes|true|1 if the converter should create'
           ' one output file for each swath (simulating a gridded L2) instead'
           ' of the original data structure (one file containing all swaths)',
           )
    return ('\n'.join(inp), '\t'.join(out))


def get_day_from_filename(input_path: str
                          ) -> datetime.datetime:
    """"""
    file_name = os.path.basename(input_path)
    name_items = file_name.split('_')
    date_str = name_items[-1]
    if date_str.startswith('v'):
        # For ASCAT data the last item contains the version number, not the
        # date.
        date_str = name_items[-2]

    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    dt = datetime.datetime(year, month, day, 0, 0, 0)
    return dt


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

    mission = input_opts.get('mission', None)
    if mission is None:
        raise MissionMissing()

    variables = input_opts.get('variables', None)
    original_var_ids = [_.strip() for _ in variables.split(',')
                        if 0 < len(_.strip())]

    required_var_ids, wind_vars = parse_wind_vars(input_opts)

    day = get_day_from_filename(input_path)

    var_ids = original_var_ids + required_var_ids
    var_ids = list(set(var_ids))
    if 0 >= len(var_ids):
        logger.warning('No variable to extract')
        raise idf_converter.lib.EarlyExit()

    with gzip.open(input_path, 'rb') as f:
        binary_data = f.read()

    offset = 0
    all_values = {}
    mappings_path = resource_filename('idf_converter',
                                      'share/remss_bytemaps.json')
    with open(mappings_path, 'r') as f:
        mappings = json.load(f)
    struct = mappings.get(mission, None)
    shape = struct['shape']
    for var_id, var_cfg in struct['vars'].items():
        add_offset = var_cfg['offset']
        scale_factor = var_cfg['scale_factor']
        valid_min = var_cfg['valid_min']
        valid_max = var_cfg['valid_max']

        count = functools.reduce(operator.mul, shape)
        packed_data = numpy.frombuffer(binary_data, dtype='ubyte',
                                       offset=offset,
                                       count=count).reshape(shape)
        offset = offset + count

        packed_data = numpy.ma.masked_where(packed_data > 250, packed_data)
        has_rain_flag = (mission in ('ascat', 'quikscat', 'seaswinds'))
        if has_rain_flag and ('RAIN' == var_id):
            suffix = var_id.replace('RAIN_', '')

            scat_rain = ((packed_data & 0x01) > 0)
            var_name = f'SCATFLAG_{suffix}'
            all_values[var_name] = {'array': scat_rain,
                                    'units': '1',
                                    'valid_min': 0,
                                    'valid_max': 1,
                                    'long_name': 'Scatterometer rain flag',
                                    'options': {}}

            adjacent_rain = ((packed_data & 0x02) > 0)
            var_name = f'RADFLAG_{suffix}'
            all_values[var_name] = {'array': adjacent_rain,
                                    'units': '1',
                                    'valid_min': 0,
                                    'valid_max': 1,
                                    'long_name': 'Collocated radiometer flag',
                                    'options': {}}

            packed_data = (packed_data & 0b11111100) >> 2

        data = add_offset + scale_factor * packed_data
        data = numpy.ma.masked_where((data < valid_min) | (data > valid_max),
                                     data)
        all_values[var_id] = {'array': data,
                              'units': var_cfg['units'],
                              'valid_min': valid_min,
                              'valid_max': valid_max,
                              'long_name': var_cfg['long_name'],
                              'options': {}}

    minutes_asc = all_values['TIME_asc']['array']
    minutes_desc = all_values['TIME_desc']['array']

    lat0 = struct['lat0']
    dlat = struct['dlat']
    lon0 = struct['lon0']
    dlon = struct['dlon']
    lat = numpy.array([lat0 + i * dlat for i in range(0, shape[0])])
    lon = numpy.array([lon0 + i * dlon for i in range(0, shape[1])])
    spatial_resolution = min([abs(dlat), abs(dlon)]) * 111000.

    use_swaths_splitting = output_opts.get('split-swaths', 'n')
    if use_swaths_splitting.lower() in ('1', 'y', 'yes'):
        asc_values = {}
        asc_units = {}
        for var_id, var_values in all_values.items():
            if var_id.endswith('_asc'):
                simple_var_id, _ = var_id.rsplit('_', 1)
                asc_values[simple_var_id] = var_values['array']
                asc_units[simple_var_id] = var_values['units']
        yield from split_swaths(input_opts, output_opts, original_var_ids,
                                day, minutes_asc, lat, lon, '_asc',
                                asc_values, asc_units, wind_vars)

        desc_values = {}
        desc_units = {}
        for var_id, var_values in all_values.items():
            if var_id.endswith('_desc'):
                simple_var_id, _ = var_id.rsplit('_', 1)
                desc_values[simple_var_id] = var_values['array']
                desc_units[simple_var_id] = var_values['units']
        yield from split_swaths(input_opts, output_opts, original_var_ids,
                                day, minutes_desc, lat, lon, '_desc',
                                desc_values, desc_units, wind_vars)
    else:
        # Time coverage
        minutes = numpy.vstack([minutes_asc, minutes_desc])
        start_minutes = int(minutes.min())
        start_dt = day + datetime.timedelta(seconds=start_minutes * 60)

        stop_minutes = int(minutes.max())
        stop_dt = day + datetime.timedelta(seconds=stop_minutes * 60)

        values = {}
        units = {}
        all_var_ids = list(all_values.keys())
        for var_id in all_var_ids:
            simple_var_id, _ = var_id.rsplit('_', 1)
            if simple_var_id in var_ids:
                values[var_id] = all_values[var_id]['array']
                units[var_id] = all_values[var_id]['units']

        granule = create_granule(input_opts, output_opts, '',
                                 start_dt, stop_dt, spatial_resolution,
                                 lat, lon, values, units)

        output_opts['__export'] = list(values.keys())

        transforms = get_wind_transforms(output_opts, wind_vars,
                                         original_var_ids, True)

        yield input_opts, output_opts, granule, transforms
