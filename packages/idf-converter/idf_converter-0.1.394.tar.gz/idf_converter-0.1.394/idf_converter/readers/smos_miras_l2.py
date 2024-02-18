# vim: ts=4:sts=4:sw=4:et
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
import datetime
import numpy.typing
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import Granule, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'GRID_LATLON'

CONTROL_BITS = {'IGNORE': 0,
                'RANGE': 1,
                'SIGMA': 2,
                'CHI2': 3,
                'CHI2_P': 4,
                'CONTAMINATED': 5,
                'SUNGLINT': 6,
                'MOONGLINT': 7,
                'GAL_NOISE': 8,
                'MIXED_SCENE': 9,
                'REACH_MAXITER': 10,
                'NUM_MEAS_MIN': 11,
                'NUM_MEAS_LOW': 12,
                'MANY_OUTLIERS': 13,
                'MARQ': 14,
                'ROUGHNESS': 15,
                'FOAM': 16,
                'ECMWF': 17,
                'VALID': 18,
                'NO_SURFACE': 19,
                'RANGE_ACARD': 20,
                'SIGMA_ACARD': 21,
                'SPARE': 22,
                'USED_FARA_TEC': 23,
                'POOR_GEOPHYSICAL': 24,
                'POOR_RETRIEVAL': 25,
                'SUSPECT_RFI': 26,
                'RFI_PRONE_X': 27,
                'RFI_PRONE_Y': 28,
                'ADJUSTED_RA': 29,
                'RETRIEV_FAIL': 30,
                'SPARE2': 31}

SCIENCE_BITS = {'LAND_SEA_COAST1': 0,
                'LAND_SEA_COAST2': 1,
                'TEC_GRADIENT': 2,
                'IN_CLIM_ICE': 3,
                'ICE': 4,
                'SUSPECT_ICE': 5,
                'RAIN': 6,
                'HIGH_WIND': 7,
                'LOW_WIND': 8,
                'HIGH_SST': 9,
                'LOW_SST': 10,
                'HIGH_SSS': 11,
                'LOW_SSS': 12,
                'SEA_STATE_1': 13,
                'SEA_STATE_2': 14,
                'SEA_STATE_3': 15,
                'SEA_STATE_4': 16,
                'SEA_STATE_5': 17,
                'SEA_STATE_6': 18,
                'SST_FRONT': 19,
                'SSS_FRONT': 20,
                'ICE_ACARD': 21,
                'ECMWF_LAND': 22}

GridIndices = typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]

# Scale factor used to circumvent underflow errors
UFLOW_FIX = 10**6


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


def get_grid_indices(lat: numpy.typing.NDArray,
                     lon: numpy.typing.NDArray,
                     x_res: float,
                     y_res: float
                     ) -> GridIndices:
    """Implement BEC method to regrid data.
    See:
    https://www.researchgate.net/publication/
    263271245_Remapping_ISEA_grid_to_lat-lon_grid_in_SMOS_context"""
    # Internal computations performed by numpy can trigger underflow errors
    # while performing divisions that invlve small numbers, so multiply both
    # the numerator and the denominator by a large number prior to computing
    # the division
    lat_rad = numpy.deg2rad(lat)
    delta = 0.5 + 1.0 * UFLOW_FIX / (2 * numpy.cos(lat_rad) * UFLOW_FIX)
    rel_i_min = -1 * delta + ((lon + 180.0) * UFLOW_FIX) / (x_res * UFLOW_FIX)
    rel_i_max = +1 * delta + ((lon + 180.0) * UFLOW_FIX) / (x_res * UFLOW_FIX)
    i_min = numpy.ceil(rel_i_min).astype('int')
    i_max = numpy.floor(rel_i_max).astype('int')
    rel_j = ((lat + 90.0) * UFLOW_FIX) / (y_res * UFLOW_FIX)
    j = numpy.floor(rel_j).astype('int')
    return (i_min, i_max, j)


def get_valid_mask(f_handler: netCDF4.Dataset,
                   lat_values: numpy.typing.NDArray,
                   sss_values: numpy.typing.NDArray
                   ) -> numpy.typing.NDArray:
    """"""
    dg_af_fov = f_handler.variables['Dg_af_fov'][:]
    control_flags = f_handler.variables['Control_Flags_corr'][:]
    science_flags = f_handler.variables['Science_Flags_corr'][:]

    control_on = numpy.int32(0)
    control_on = control_on + numpy.int32(1 << CONTROL_BITS['ECMWF'])

    control_off = numpy.int32(0)
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['CHI2_P'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['SUNGLINT'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['MOONGLINT'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['REACH_MAXITER'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['NUM_MEAS_MIN'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['NUM_MEAS_LOW'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['MANY_OUTLIERS'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['MARQ'])
    control_off = control_off + numpy.int32(1 << CONTROL_BITS['SUSPECT_RFI'])

    ctrl_on_mask = (numpy.bitwise_and(control_on, control_flags) == control_on)
    ctrl_off_mask = (numpy.bitwise_and(control_off, control_flags) == 0)
    control_valid = (ctrl_on_mask & ctrl_off_mask)

    science_on = numpy.int32(0)
    science_on = science_on + numpy.int32(1 << SCIENCE_BITS['LAND_SEA_COAST1'])
    science_on = science_on + numpy.int32(1 << SCIENCE_BITS['LOW_WIND'])

    science_off = numpy.int32(0)
    science_off = science_off + numpy.int32(1 << SCIENCE_BITS['ICE'])
    science_off = science_off + numpy.int32(1 << SCIENCE_BITS['SUSPECT_ICE'])

    sci_on_mask = (numpy.bitwise_and(science_on, science_flags) == science_on)
    sci_off_mask = (numpy.bitwise_and(science_off, science_flags) == 0)
    science_valid = (sci_on_mask & sci_off_mask)

    af_fov_valid = (dg_af_fov > 130.0)

    sss_invalid_mask = (sss_values == -999)
    sss_below_25_mask: numpy.typing.NDArray[numpy.bool_] = (sss_values < 25.0)
    sss_below_30_mask: numpy.typing.NDArray[numpy.bool_] = (sss_values < 30.0)
    sss_above_40_mask: numpy.typing.NDArray[numpy.bool_] = (sss_values > 40.0)
    sss_lowlat_invalid_mask = ((numpy.abs(lat_values) <= 30.0) &
                               (sss_below_25_mask | sss_above_40_mask))
    sss_high_lat_invalid_mask = ((numpy.abs(lat_values) > 30.0) &
                                 (sss_below_30_mask | sss_above_40_mask))
    sss_invalid = (sss_invalid_mask | sss_lowlat_invalid_mask |
                   sss_high_lat_invalid_mask)

    valid_mask: numpy.typing.NDArray = (~sss_invalid &
                                        af_fov_valid &
                                        control_valid &
                                        science_valid)

    return valid_mask


def regrid_data(nlat: int,
                nlon: int,
                lat1d: numpy.typing.NDArray,
                lon1d: numpy.typing.NDArray,
                values1d: typing.Dict[str, numpy.typing.NDArray],
                valid_mask: numpy.typing.NDArray,
                granule: Granule
                ) -> typing.Tuple[numpy.typing.NDArray, numpy.typing.NDArray]:
    x_res = 360.0 / nlon
    y_res = 180.0 / nlat
    valid_ind = numpy.where(valid_mask == True)  # noqa
    valid_lat1d = lat1d[valid_ind]
    valid_lon1d = lon1d[valid_ind]
    regridded_points = get_grid_indices(valid_lat1d, valid_lon1d, x_res, y_res)

    i_lowers, i_uppers, js = regridded_points
    for var_name in values1d.keys():
        valid_var_values = values1d[var_name][valid_ind]
        _var_grid = numpy.full((nlat, nlon), 0.0, dtype=float)
        var_grid = numpy.ma.array(_var_grid)
        count_grid = numpy.full((nlat, nlon), 0, dtype=numpy.int32)
        for k, j in enumerate(js):
            i_min = i_lowers[k]
            i_max = i_uppers[k]
            if i_min >= i_max:
                i = numpy.mod(i_min, nlon).astype('int')
                count_grid[j, i] += 1
                var_grid[j, i] += valid_var_values[k]
            else:
                for _i in range(i_min, i_max):
                    i = numpy.mod(_i, nlon).astype('int')
                    count_grid[j, i] += 1
                    var_grid[j, i] += valid_var_values[k]

        # Compute mean for each cell
        positive_count_ind = numpy.where(count_grid > 0)
        var_sum = var_grid[positive_count_ind]
        count = count_grid[positive_count_ind]
        var_grid[positive_count_ind] = var_sum / count
        var_grid.mask = (count_grid <= 0)

        granule.vars[var_name]['array'] = var_grid

    # Locate surrounding rows and columns that contain no valid data in order
    # to compute the actual bounding box
    mask: numpy.typing.NDArray[numpy.bool_] = (count_grid <= 0)
    cols_mask = numpy.logical_and.reduce(mask, axis=0)
    rows_mask = numpy.logical_and.reduce(mask, axis=1)
    valid_cols_ind = numpy.where(~cols_mask)
    valid_rows_ind = numpy.where(~rows_mask)
    if 0 >= len(valid_rows_ind[0]):
        logger.warning('No valid data to process')
        raise idf_converter.lib.EarlyExit()

    lat_slice = slice(valid_rows_ind[0][0], 1 + valid_rows_ind[0][-1])
    lon_slice = slice(valid_cols_ind[0][0], 1 + valid_cols_ind[0][-1])
    lat0 = -90.0 + lat_slice.start * y_res
    lon0 = -180.0 + lon_slice.start * x_res

    # Geolocation is expected to be located at the pixel center by default
    actual_nlat = lat_slice.stop - lat_slice.start
    actual_nlon = lon_slice.stop - lon_slice.start
    lat = numpy.array([lat0 + (i + 0.5) * y_res for i in range(actual_nlat)])
    lon = numpy.array([lon0 + (i + 0.5) * x_res for i in range(actual_nlon)])

    # Crop data out of the bounding box to reduce the size of the output file.
    for var_name in granule.vars.keys():
        var_data = granule.vars[var_name]['array']
        granule.vars[var_name]['array'] = var_data[(lat_slice, lon_slice)]

    # print(lat.size, lon.size, numpy.shape(granule.vars['SSS_corr']['array']))
    return lat, lon


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

    variables = {'SSS_corr': {'name': 'SSS_corr',
                              'valid_min': 25.0,
                              'valid_max': 40.0,
                              'options': {}},
                 'SSS_climatology': {'name': 'SSS_climatology',
                                     'valid_min': 0.0,
                                     'valid_max': 40.0,
                                     'options': {}},
                 'WS': {'name': 'WS',
                        'valid_min': 0.0,
                        'valid_max': 50.0,
                        'options': {}},
                 'SST': {'name': 'SST',
                         'valid_min': -2.10,
                         'valid_max': 36.0,
                         'options': {}}}

    channels = list(variables.keys())

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    _nlat = input_opts.get('grid_height', None)
    nlat = int(_nlat)

    _nlon = input_opts.get('grid_width', None)
    nlon = int(_nlon)

    values1d = {}
    f_handler = netCDF4.Dataset(input_path, 'r')
    lon1d = idf_converter.lib.extract_variable_values(f_handler, 'Longitude')
    lat1d = idf_converter.lib.extract_variable_values(f_handler, 'Latitude')
    for var_id in channels:
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        values1d[var_id] = _band

    valid_mask = get_valid_mask(f_handler, lat1d, values1d['SSS_corr'])
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    start_attr_name = 'Fixed_Header:Validity_Period:Validity_Start'
    start_str = f_handler.getncattr(start_attr_name)
    stop_attr_name = 'Fixed_Header:Validity_Period:Validity_Stop'
    stop_str = f_handler.getncattr(stop_attr_name)
    f_handler.close()

    lat, lon = regrid_data(nlat, nlon, lat1d, lon1d, values1d, valid_mask,
                           granule)

    granule.dims['lat'] = lat.size
    granule.dims['lon'] = lon.size
    dlon = 360.0 / nlon
    dlat = 180.0 / nlat
    spatial_resolution = min([abs(dlat), abs(dlon)]) * 111000.

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = datetime.datetime.strptime(start_str[4:], '%Y-%m-%dT%H:%M:%S')
    stop_dt = datetime.datetime.strptime(stop_str[4:], '%Y-%m-%dT%H:%M:%S')

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_resolution
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'DPGS'
    granule.meta['platform'] = 'SMOS'
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'MIRAS'

    # Add transforms
    transforms: TransformsList = []

    output_opts['__export'] = channels

    yield (input_opts, output_opts, granule, transforms)
