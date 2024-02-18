# vim: ts=4:sts=4:sw=4
#
# @date 2021-12-28
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
import pyproj
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import ReaderResult, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'time_dependent'
VARS_IN_KNOTS = ('wind',)
VARS_IN_MB = ('pres',)
VARS_IN_NM = ('r34_ne', 'r34_se', 'r34_sw', 'r34_nw', 'r50_ne', 'r50_se',
              'r50_sw', 'r50_nw', 'r64_ne', 'r64_se', 'r64_sw', 'r64_nw',
              'rmw')


class InputPathMissing(ValueError):
    """Error raised when the input options have no "path" entry"""
    pass


class NotEnoughData(Exception):
    """Error raised when the input data has less than 3 values, which is the
    minimal values count supported by this reader."""
    def __init__(self) -> None:
        """"""
        msg = 'This reader requires at least three along-track values'
        super(NotEnoughData, self).__init__(msg)


class StormNameMissing(Exception):
    """Error raised when the storm name variable contains only empty values."""
    def __init__(self, storm_id: str) -> None:
        """"""
        self.storm_id = storm_id


class StormNameConflict(Exception):
    """Error raised when the storm name variable contains different, non-empty
    values."""
    def __init__(self, storm_id: str) -> None:
        """"""
        self.storm_id = storm_id


class StormATCFIDMissing(Exception):
    """Error raised when the storm ATCF identifier variable contains only empty
    values."""
    def __init__(self, storm_id: str) -> None:
        """"""
        self.storm_id = storm_id


class StormATCFIDConflict(Exception):
    """Error raised when the storm ATCF identifier variable contains different,
    non-empty values."""
    def __init__(self, storm_id: str) -> None:
        """"""
        self.storm_id = storm_id


class InvalidMaxTranslationSpeed(ValueError):
    """Error raised when the value passed for the max_translation_speed input
    option cannot be parsed as a float."""
    def __init__(self, value: str) -> None:
        """"""
        self.invalid_value = value


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           '    max_translation_mps\tThreshold for the storm translation '
           'speed: observations for which the translation speed exceeds the '
           'threshold will be discarded. Expressed in meter per second, '
           'default value: 83.3333 (i.e. 300km/h)')
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
    _convertutc = datetime.datetime.utcfromtimestamp

    variables = {'wind': {'name': 'wind'},
                 'pres': {'name': 'pressure'},
                 'r34_ne': {'name': 'r34_ne'},
                 'r34_se': {'name': 'r34_se'},
                 'r34_sw': {'name': 'r34_sw'},
                 'r34_nw': {'name': 'r34_nw'},
                 'r50_ne': {'name': 'r50_ne'},
                 'r50_se': {'name': 'r50_se'},
                 'r50_sw': {'name': 'r50_sw'},
                 'r50_nw': {'name': 'r50_nw'},
                 'r64_ne': {'name': 'r64_ne'},
                 'r64_se': {'name': 'r64_se'},
                 'r64_sw': {'name': 'r64_sw'},
                 'r64_nw': {'name': 'r64_nw'},
                 'rmw': {'name': 'rmax'},
                 }

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    max_mps_str = input_opts.get('max_translation_mps', str(300000 / 3600))
    try:
        max_mps = float(max_mps_str)
    except ValueError:
        raise InvalidMaxTranslationSpeed(max_mps_str)

    granule.vars = variables
    channels = list(variables.keys())

    spatial_res_meters = 1.e07

    f_handler = netCDF4.Dataset(input_path, 'r')
    _time = idf_converter.lib.extract_variable_values(f_handler, 'time')
    _lon = idf_converter.lib.extract_variable_values(f_handler, 'lon')
    _lat = idf_converter.lib.extract_variable_values(f_handler, 'lat')
    _atcf_id = netCDF4.chartostring(f_handler.variables['atcf_id'][:])
    _sid = netCDF4.chartostring(f_handler.variables['sid'][:])
    _name = netCDF4.chartostring(f_handler.variables['name'][:])

    _lon_mask = numpy.ma.getmaskarray(_lon)
    if _lon_mask.any():
        logger.warning(f'Masked longitudes in {input_path}')
    _lon = numpy.ma.getdata(_lon)

    _lat_mask = numpy.ma.getmaskarray(_lat)
    if _lat_mask.any():
        logger.warning(f'Masked latitudes in {input_path}')
    _lat = numpy.ma.getdata(_lat)

    _time_mask = numpy.ma.getmaskarray(_time)
    if _time_mask.any():
        logger.warning(f'Masked times in {input_path}')
    _time = numpy.ma.getdata(_time)

    # Apply time offset to transform time into an EPOCH timestamp
    ref_time = datetime.datetime(2010, 1, 1, 12, 0, 0)
    epoch = datetime.datetime(1970, 1, 1)
    time_offset = (ref_time - epoch).total_seconds()
    shifted_time = numpy.int_(time_offset) + _time * 60
    _time = shifted_time.astype(numpy.double)

    # Extract data variables
    _data = {}
    for var_id in granule.vars.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        _data[var_id] = band
    f_handler.close()

    # Group observations based on storm identifiers
    sorted_ind = _sid.argsort(0)
    sorted_sid = _sid[sorted_ind]
    unique_sid, sid_slice_start = numpy.unique(sorted_sid, return_index=True)
    sid_ind = numpy.split(sorted_ind, sid_slice_start[1:])

    geod = pyproj.Geod(ellps='WGS84')
    for i, storm_id in enumerate(unique_sid):
        # Reorder indices associated to this storm by ascending time
        storm_ind = sid_ind[i]
        unsorted_storm_time = _time[storm_ind]
        time_sorted_storm_ind = storm_ind[unsorted_storm_time.argsort(0)]

        storm_time = _time[time_sorted_storm_ind]
        storm_lat = _lat[time_sorted_storm_ind]
        storm_lon = _lon[time_sorted_storm_ind]

        # Longitude continuity fix (required for distance computation later on)
        lon0 = numpy.mean(storm_lon)
        storm_lon = lon0 + numpy.mod(storm_lon - lon0, 360)
        storm_lon[numpy.where(storm_lon > lon0 + 180)] -= 360
        storm_lon[numpy.where(storm_lon < lon0 - 180)] += 360

        storm_data = {}
        for var_id in variables:
            storm_data[var_id] = _data[var_id][time_sorted_storm_ind]

        # Remove outliers (translation speed above 150km/h)
        dists = geod.line_lengths(storm_lon, storm_lat)
        storm_dtime = storm_time[1:] - storm_time[:-1]
        outliers_ind = numpy.where(dists > storm_dtime * max_mps)
        while 0 < len(outliers_ind[0]):
            del_ind = outliers_ind[0][0] + 1
            logger.warning(f'Removing outlier for {storm_id}: '
                           f'at {storm_lon[del_ind]}, {storm_lat[del_ind]}')

            # remove outlier from coordinates and variables
            storm_time = numpy.delete(storm_time, del_ind)
            storm_lon = numpy.delete(storm_lon, del_ind)
            storm_lat = numpy.delete(storm_lat, del_ind)
            for var_id in variables:
                storm_data[var_id] = numpy.delete(storm_data[var_id], del_ind)

            # detect remaining outliers
            dists = geod.line_lengths(storm_lon, storm_lat)
            storm_dtime = storm_time[1:] - storm_time[:-1]
            outliers_ind = numpy.where(dists > storm_dtime * max_mps)

        # extract a single name for the storm
        _storm_name = _name[time_sorted_storm_ind]
        non_empty_ind = numpy.where(_storm_name != '')
        _storm_name = numpy.unique(_storm_name[non_empty_ind])
        if 0 >= _storm_name.size:
            raise StormNameMissing(storm_id)
        elif 1 < _storm_name.size:
            raise StormNameConflict(storm_id)
        storm_name = _storm_name[0]

        # extract a single ATCF identifier for the storm
        _storm_atcf_id = _atcf_id[time_sorted_storm_ind]
        non_empty_ind = numpy.where(_storm_atcf_id != '')
        _storm_atcf_id = numpy.unique(_storm_atcf_id[non_empty_ind])
        storm_atcf_id = None
        if 1 < _storm_atcf_id.size:
            raise StormATCFIDConflict(storm_id)
        elif 1 == _storm_atcf_id.size:
            storm_atcf_id = _storm_atcf_id[0]

        storm_granule = idf_converter.lib.create_granule(idf_version,
                                                         DATA_MODEL)

        for var_id in variables:
            storm_granule.vars[var_id] = {'options': {}}

            # Copy attributes from the "main" granule object
            for attr_name, attr_value in granule.vars[var_id].items():
                if 'array' == attr_name:
                    continue
                storm_granule.vars[var_id][attr_name] = attr_value

            band = storm_data[var_id]
            vmin = storm_granule.vars[var_id]['valid_min']
            vmax = storm_granule.vars[var_id]['valid_max']

            # 1 knot = 1 international nautical mile per hour
            if var_id in VARS_IN_KNOTS:
                band = band * numpy.float64(1852.0 / 3600.0)
                storm_granule.vars[var_id]['units'] = 'm.s-1'
                storm_granule.vars[var_id]['valid_min'] = vmin * 1852 / 3600
                storm_granule.vars[var_id]['valid_max'] = vmax * 1852 / 3600

            # 1 international nautical mile = 1852 meters
            if var_id in VARS_IN_NM:
                band = band * 1852
                storm_granule.vars[var_id]['units'] = 'm'
                storm_granule.vars[var_id]['valid_min'] = vmin * 1852
                storm_granule.vars[var_id]['valid_max'] = vmax * 1852

            # 1 millibar = 100 Pa
            if var_id in VARS_IN_MB:
                band = band * 100
                storm_granule.vars[var_id]['units'] = 'Pa'
                storm_granule.vars[var_id]['valid_min'] = vmin * 100
                storm_granule.vars[var_id]['valid_max'] = vmax * 100

            storm_granule.vars[var_id]['array'] = band

        # Add coordinates variables
        storm_granule.vars['lat'] = {'units': 'degrees north',
                                     'array': storm_lat,
                                     'datatype': _lat.dtype,
                                     'options': {}}
        storm_granule.vars['lon'] = {'units': 'degrees east',
                                     'array': storm_lon,
                                     'datatype': _lon.dtype,
                                     'options': {}}

        out_time_units = 'seconds since 1970-01-01T00:00:00.000Z'
        storm_granule.vars['time'] = {'units': out_time_units,
                                      'array': storm_time,
                                      'datatype': numpy.double,
                                      'options': {}}

        # Set Global parameters
        granule_name = os.path.splitext(os.path.basename(input_path))[0]
        storm_granule.meta['idf_subsampling_factor'] = 0
        storm_granule.meta['idf_spatial_resolution'] = spatial_res_meters
        storm_granule.meta['idf_spatial_resolution_units'] = 'm'

        if storm_atcf_id is not None:
            storm_granule.meta['atcf_id'] = storm_atcf_id
        storm_granule.meta['storm_name'] = storm_name
        storm_granule.meta['storm_id'] = storm_id

        start_dt = _convertutc(storm_time[0])
        stop_dt = _convertutc(storm_time[-1])
        if storm_name not in ('', 'NOT NAMED', 'NOT_NAMED'):
            _granule_name = f'{storm_id}_{storm_name}_{granule_name}'
        else:
            _granule_name = f'{storm_id}_{granule_name}'
        storm_granule.meta['idf_granule_id'] = f'{_granule_name}'
        storm_granule.meta['time_coverage_start'] = start_dt
        storm_granule.meta['time_coverage_end'] = stop_dt

        transforms: TransformsList = []

        transforms.append(('remove_extra_lon_degrees', {'lon_name': 'lon'}))

        output_opts['__export'] = channels

        # data_model, dims, vars, attrs, formatter_jobs
        yield (input_opts, output_opts, storm_granule, transforms)
