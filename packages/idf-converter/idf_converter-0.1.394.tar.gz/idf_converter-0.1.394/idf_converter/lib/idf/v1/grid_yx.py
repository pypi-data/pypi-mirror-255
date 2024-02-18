# vim: set ts=4:sts=4:sw=4
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
import pyproj
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


class MissingProjection(Exception):
    """"""
    pass


def get_projection(proj_def: typing.Any) -> pyproj.Proj:
    """"""
    proj = pyproj.Proj(proj_def)
    return proj


def help() -> typing.Tuple[str, str]:
    """"""
    inp = ('    geoloc_at_pixel_center\tBoolean set to true if the coordinates'
           ' provided in the input file correspond to the center of the pixels'
           ' and to false if they are referencing the top-left corner of the'
           ' pixels',
           )

    out = ('    gcp_spacing\tTODO',
           '    gcp_y_spacing\tTODO',
           '    gcp_x_spacing\tTODO',
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
    gcp_y_spacing = int(output_opts.get('gcp_y_spacing', gcp_spacing))
    gcp_x_spacing = int(output_opts.get('gcp_x_spacing', gcp_spacing))

    proj_def = input_opts.get('projection', None)
    if proj_def is None:
        raise MissingProjection()

    proj = get_projection(proj_def)

    ny = granule.dims['y']
    nx = granule.dims['x']

    # Compute GCPs
    has_yx = (('y' in granule.vars.keys()) and ('x' in granule.vars.keys()))
    has_latlon = (('lat' in granule.vars.keys()) and
                  ('lon' in granule.vars.keys()))

    if has_yx:
        y = granule.vars['y']['array']
        x = granule.vars['x']['array']
        if 1 == len(numpy.shape(x)):
            mesh_x, mesh_y = numpy.meshgrid(x, y)
        else:
            mesh_x, mesh_y = x, y
    elif has_latlon:
        lat = granule.vars['lat']['array']
        lon = granule.vars['lon']['array']

        # Convert coordinates to y/x projection where the distance between
        # adjacent data row/cell is fixed
        if 1 == len(numpy.shape(lon)):
            mesh_lon, mesh_lat = numpy.meshgrid(lon, lat)
        else:
            mesh_lon, mesh_lat = lon, lat

        mesh_x, mesh_y = proj(mesh_lon, mesh_lat)

    # Compute geotransform parameters
    # A workaround is used here to avoid numerical precision issues in
    # numpy.mean: if values are too close to 0, underflow errors may arise so
    # we multiply values by a large factor before passing them to numpy.mean,
    # then we divide the result by the same factor
    _use_mean_dydx = output_opts.get('use_mean_dydx', 'no')
    use_mean_dydx = (_use_mean_dydx.lower() in ('yes', 'true'))
    try:
        mesh_dx = mesh_x[:, 1:] - mesh_x[:, :-1]
        mesh_dy = mesh_y[1:, :] - mesh_y[:-1, :]
        if use_mean_dydx:
            _dx = numpy.mean(mesh_dx)
            _dy = numpy.mean(mesh_dy)
        else:
            unique_dx, count_dx = numpy.unique(mesh_dx, return_counts=True)
            unique_dy, count_dy = numpy.unique(mesh_dy, return_counts=True)
            _dx = unique_dx[count_dx.argmax()]
            _dy = unique_dy[count_dy.argmax()]
        _x0 = mesh_x[0, 0]
        _y0 = mesh_y[0, 0]
    except FloatingPointError:
        precision_factor = 10000
        mean_x = numpy.mean(precision_factor * mesh_x, axis=0)
        mean_y = numpy.mean(precision_factor * mesh_y, axis=1)
        _dx = numpy.mean(mean_x[1:] - mean_x[:-1]) / precision_factor
        _dy = numpy.mean(mean_y[1:] - mean_y[:-1]) / precision_factor
        _x0 = mean_x[0] / precision_factor
        _y0 = mean_y[0] / precision_factor
    x0, dxx, dxy, y0, dyx, dyy = [_x0, _dx, 0, _y0, 0, _dy]

    # Compute number of GCPs (except the ones for bottom and right edge)
    # according to the requested resolution, i.e. the number of digital points
    # between two GCPs
    gcp_ny = numpy.ceil(ny / gcp_y_spacing).astype('int')
    gcp_nx = numpy.ceil(nx / gcp_x_spacing).astype('int')

    logger.debug(f'{ny}, {nx}, {gcp_y_spacing}, {gcp_x_spacing},'
                 f'{gcp_ny}, {gcp_nx}')

    # Compute matrix indices for the GCPs
    gcp_lin = numpy.arange(gcp_ny) * gcp_y_spacing
    gcp_pix = numpy.arange(gcp_nx) * gcp_x_spacing

    # Add an extra line and column to geolocate the bottom and right edges of
    # the data matrix
    gcp_lin = numpy.concatenate((gcp_lin, [ny]))
    gcp_pix = numpy.concatenate((gcp_pix, [nx]))

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

    # Compute GCP geographical coordinates expressed in y/x projection
    _gcp_lin = gcp_lin[:, numpy.newaxis]
    _gcp_pix = gcp_pix[numpy.newaxis, :]
    gcp_y = y0 + dyx * _gcp_pix + dyy * _gcp_lin
    gcp_x = x0 + dxx * _gcp_pix + dxy * _gcp_lin

    # Convert GCP geographical coordinates from y/x projection to lat/lon
    gcp_lon, gcp_lat = proj(gcp_x, gcp_y, inverse=True)

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
    gcp_ny, gcp_nx = gcp_lin.size, gcp_pix.size

    ny = granule.dims['y']
    nx = granule.dims['x']

    # Central datetime
    _start_dt = granule.meta['time_coverage_start']
    _stop_dt = granule.meta['time_coverage_end']
    mid_time = _start_dt + (_stop_dt - _start_dt) / 2

    # Precision set to seconds
    # TODO: check if this is really necessary (a double value should be enough
    # to store whole seconds and decimals up to microseconds)
    microseconds = mid_time.microsecond
    if microseconds > 500000:
        mid_time = mid_time + datetime.timedelta(seconds=1)
    mid_time = mid_time.replace(microsecond=0)

    # Dimensions
    idf_file.createDimension('time', None)  # unlimited
    idf_file.createDimension('y', ny)
    idf_file.createDimension('x', nx)
    idf_file.createDimension('y_gcp', gcp_ny)
    idf_file.createDimension('x_gcp', gcp_nx)
    idf_dims = ('time', 'y', 'x', 'y_gcp', 'x_gcp',)
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

    _latgcp = idf_file.createVariable('lat_gcp', 'f4', ('y_gcp', 'x_gcp'))
    _latgcp.long_name = 'ground control points latitude'
    _latgcp.standard_name = 'latitude'
    _latgcp.units = 'degrees_north'
    _latgcp[:] = gcp_lat[:, :].astype('float32')

    _longcp = idf_file.createVariable('lon_gcp', 'f4', ('y_gcp', 'x_gcp'))
    _longcp.long_name = 'ground control points longitude'
    _longcp.standard_name = 'longitude'
    _longcp.units = 'degrees_east'
    _longcp[:] = gcp_lon[:, :].astype('float32')

    _indexlatgcp = idf_file.createVariable('index_y_gcp', 'i4', ('y_gcp',))
    _indexlatgcp.long_name = 'index of ground control points in y dimension'
    _indexlatgcp.comment = ('index goes from 0 (start of first pixel) to '
                            'dimension value (end of last pixel)')
    _indexlatgcp[:] = gcp_lin.astype('int32')

    _indexlongcp = idf_file.createVariable('index_x_gcp', 'i4', ('x_gcp',))
    _indexlongcp.long_name = 'index of ground control points in x dimension'
    _indexlongcp.comment = ('index goes from 0 (start of first pixel) to '
                            'dimension value (end of last pixel)')
    _indexlongcp[:] = gcp_pix.astype('int32')

    crs = idf_file.createVariable('crs', 'i4')
    proj_def = input_opts['projection']
    proj = get_projection(proj_def)
    for key, value in proj.crs.to_cf().items():
        setattr(crs, key, value)

    idf_file.cdm_data_type = b'Grid'

    processed_dims = ['time', 'y', 'x', 'y_gcp', 'x_gcp']
    processed_vars = ['time', 'lat_gcp', 'lon_gcp', 'index_y_gcp',
                      'index_x_gcp', 'lat', 'lon', 'y', 'x']
    processed_attrs = ['cdm_data_type']

    return (processed_dims, processed_vars, processed_attrs)
