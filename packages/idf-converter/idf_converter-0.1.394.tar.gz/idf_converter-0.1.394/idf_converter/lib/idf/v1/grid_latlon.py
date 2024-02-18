# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-25
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
import netCDF4
import datetime
from idf_converter.lib.types import InputOptions, OutputOptions, ProcessedLists
from idf_converter.lib.types import Granule, FormatterResult

logger = logging.getLogger(__name__)
GCPs = typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]


class MultipleDepthValues(Exception):
    """Error raised when the depth dimension is defined and its size is greater
    than 1: a single depth has to be selected in the reader!
    """
    pass


def help() -> typing.Tuple[str, str]:
    """"""
    inp = ('    geoloc_at_pixel_center\tBoolean set to true if the coordinates'
           ' provided in the input file correspond to the center of the pixels'
           ' and to false if they are referencing the top-left corner of the'
           ' pixels',
           )

    out = ('    gcp_spacing\tTODO',
           '    gcp_lat_spacing\tTODO',
           '    gcp_lon_spacing\tTODO',
           )
    return ('\n'.join(inp), '\n'.join(out))


def preformat(input_opts: InputOptions, output_opts: OutputOptions,
              granule: Granule) -> typing.Iterator[FormatterResult]:
    """"""
    if 'depth' in granule.dims.keys() and 'depth' in granule.vars.keys():
        if 1 < granule.dims['depth']:
            raise MultipleDepthValues()

        del granule.dims['depth']
        depth_var = granule.vars.pop('depth')
        depth = depth_var['array']
        granule_id = granule.meta['idf_granule_id']
        granule.meta['idf_granule_id'] = f'depth_{depth[0]}m_{granule_id}'

        granule.meta['geospatial_vertical_min'] = depth[0]
        granule.meta['geospatial_vertical_max'] = depth[0]
        if 'units' in depth_var.keys():
            depth_units = depth_var['units']
            granule.meta['geospatial_vertical_units'] = depth_units
        if 'positive' in depth_var.keys():
            depth_pos = depth_var['positive']
            granule.meta['geospatial_vertical_positive'] = depth_pos

    yield input_opts, output_opts, granule


def compute_gcps(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 granule: Granule) -> GCPs:
    """"""
    # Number of digital points per GCP
    gcp_spacing = int(output_opts.get('gcp_spacing', 32))
    gcp_lat_spacing = int(output_opts.get('gcp_lat_spacing', gcp_spacing))
    gcp_lon_spacing = int(output_opts.get('gcp_lon_spacing', gcp_spacing))

    nlat = granule.dims['lat']
    nlon = granule.dims['lon']

    # Compute GCPs
    lon = granule.vars['lon']['array']
    lat = granule.vars['lat']['array']

    # Handle longitude continuity
    dlon = lon[1:] - lon[:-1]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon_neg_ind = numpy.where(lon < 0.0)
        lon[lon_neg_ind] = lon[lon_neg_ind] + 360.0

    # Compute geotransform parameters
    # A workaround is used here to avoid numerical precision issues in
    # numpy.mean: if values are too close to 0, underflow errors may arise so
    # we multiply values by a large factor before passing them to numpy.mean,
    # then we divide the result by the same factor
    precision_factor = 10000
    lon0 = lon[0]
    _dlon = lon[1:] - lon[:-1]
    try:
        dlon = numpy.mean(_dlon)
    except FloatingPointError:
        dlon = numpy.mean(precision_factor * _dlon) / precision_factor
    lat0 = lat[0]
    _dlat = lat[1:] - lat[:-1]
    try:
        dlat = numpy.mean(_dlat)
    except FloatingPointError:
        dlat = numpy.mean(precision_factor * _dlat) / precision_factor
    x0, dxx, dxy, y0, dyx, dyy = [lon0, dlon, 0, lat0, 0, dlat]

    logger.debug(f'Geotransform: {x0} {dxx} {dxy} {y0} {dyx} {dyy}')

    # Compute number of GCPs (except the ones for bottom and right edge)
    # according to the requested resolution, i.e. the number of digital points
    # between two GCPs
    gcp_nlat = numpy.ceil(nlat / gcp_lat_spacing).astype('int')
    gcp_nlon = numpy.ceil(nlon / gcp_lon_spacing).astype('int')

    logger.debug(f'{nlat}, {nlon}, {gcp_lat_spacing}, {gcp_lon_spacing},'
                 f'{gcp_nlat}, {gcp_nlon}')

    # Compute matrix indices for the GCPs
    gcp_lin = numpy.arange(gcp_nlat) * gcp_lat_spacing
    gcp_pix = numpy.arange(gcp_nlon) * gcp_lon_spacing

    # Add an extra line and column to geolocate the bottom and right edges of
    # the data matrix
    gcp_lin = numpy.concatenate((gcp_lin, [nlat]))
    gcp_pix = numpy.concatenate((gcp_pix, [nlon]))

    # GCP pixels are located at the edge of data pixels, meaning that the
    # center of the first data pixel is located at (0.5, 0.5) in the GCPs
    # matrix.
    # If lon/lat correspond to the center of data pixels, then the indices
    # stored in the GCPs must be shifted by one half-pixel along each axis
    _geoloc_at_pixel_center = input_opts.get('geoloc_at_pixel_center', 'true')
    geoloc_at_pixel_center = _geoloc_at_pixel_center.lower() in ('true', 'yes')
    if geoloc_at_pixel_center:
        logger.debug('Shift GCPs by ½ pixel')
        x0 = x0 - 0.5 * dxx
        y0 = y0 - 0.5 * dyy

    # Compute GCP geographical coordinates expressed in lat/lon
    _gcp_lin = gcp_lin[:, numpy.newaxis]
    _gcp_pix = gcp_pix[numpy.newaxis, :]
    gcp_lat = y0 + dyx * _gcp_pix + dyy * _gcp_lin
    gcp_lon = x0 + dxx * _gcp_pix + dxy * _gcp_lin

    return gcp_lon, gcp_lat, gcp_lin, gcp_pix


def format_granule(input_opts: InputOptions,
                   output_opts: OutputOptions,
                   granule: Granule,
                   idf_file: netCDF4.Dataset) -> ProcessedLists:
    """Create dimensions, variables and attributes required for swath granules.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.Granule
        Object representing the granule data and metadata
    idf_file: netCDF4.Dataset
        Handle of the IDF file to edit

    Returns
    -------
    tuple
        Information about granule information that the method has processed.
        The tuple contains three lists::
        - a list of names for the dimensions created by the method
        - a list of identifiers for the variables created by the method
        - a list of names for the attributes created by the method
    """

    gcp_lon, gcp_lat, gcp_lin, gcp_pix = compute_gcps(input_opts, output_opts,
                                                      granule)
    gcp_nlat, gcp_nlon = gcp_lin.size, gcp_pix.size

    nlat = granule.dims['lat']
    nlon = granule.dims['lon']

    # Central datetime
    _start_dt = granule.meta['time_coverage_start']
    _stop_dt = granule.meta['time_coverage_end']
    mid_time = _start_dt + (_stop_dt - _start_dt) / 2

    # Precision set to seconds
    microseconds = mid_time.microsecond
    if microseconds > 500000:
        mid_time = mid_time + datetime.timedelta(seconds=1)
    mid_time = mid_time.replace(microsecond=0)

    # Dimensions
    idf_file.createDimension('time', None)  # unlimited
    idf_file.createDimension('lat', nlat)
    idf_file.createDimension('lon', nlon)
    idf_file.createDimension('lat_gcp', gcp_nlat)
    idf_file.createDimension('lon_gcp', gcp_nlon)
    idf_dims = ('time', 'lat', 'lon', 'lat_gcp', 'lon_gcp',)
    extra_dims = [x for x in granule.dims.keys() if x not in idf_dims]
    for extra_dim in extra_dims:
        idf_file.createDimension(extra_dim, granule.dims[extra_dim])

    # Variables
    _time = idf_file.createVariable('time', 'f8', ('time', ))
    _time.long_name = 'time'
    _time.standard_name = 'time'
    _time.units = 'seconds since 1970-01-01T00:00:00.000000Z'
    _time.calendar = 'standard'
    _time[:] = (mid_time - datetime.datetime(1970, 1, 1)).total_seconds()

    _latgcp = idf_file.createVariable('lat_gcp', 'f4', ('lat_gcp',))
    _latgcp.long_name = 'ground control points latitude'
    _latgcp.standard_name = 'latitude'
    _latgcp.units = 'degrees_north'
    _latgcp[:] = gcp_lat[:, 0].astype('float32')

    _longcp = idf_file.createVariable('lon_gcp', 'f4', ('lon_gcp',))
    _longcp.long_name = 'ground control points longitude'
    _longcp.standard_name = 'longitude'
    _longcp.units = 'degrees_east'
    _longcp[:] = gcp_lon[0, :].astype('float32')

    _indexlatgcp = idf_file.createVariable('index_lat_gcp', 'i4', ('lat_gcp',))
    _indexlatgcp.long_name = ('index of ground control points in lat '
                              'dimension')
    _indexlatgcp.comment = ('index goes from 0 (start of first pixel) to '
                            'dimension value (end of last pixel)')
    _indexlatgcp[:] = gcp_lin.astype('int32')

    _indexlongcp = idf_file.createVariable('index_lon_gcp', 'i4', ('lon_gcp',))
    _indexlongcp.long_name = 'index of ground control points in lon dimension'
    _indexlongcp.comment = ('index goes from 0 (start of first pixel) to '
                            'dimension value (end of last pixel)')
    _indexlongcp[:] = gcp_pix.astype('int32')

    idf_file.cdm_data_type = b'Grid'

    processed_dims = ['time', 'lat', 'lon', 'lat_gcp', 'lon_gcp']
    processed_vars = ['time', 'lat_gcp', 'lon_gcp', 'index_lat_gcp',
                      'index_lon_gcp', 'lat', 'lon']
    processed_attrs = ['cdm_data_type']

    return (processed_dims, processed_vars, processed_attrs)
