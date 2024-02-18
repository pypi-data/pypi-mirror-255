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
import numpy.typing
import typing
import logging
import netCDF4
import datetime
import idf_converter.lib.constants
import idf_converter.lib.interp
from idf_converter.lib.geo import _fix_swath_longitudes, fix_swath_longitudes
from idf_converter.lib.types import InputOptions, OutputOptions, ProcessedLists
from idf_converter.lib.types import Granule, FormatterResult

logger = logging.getLogger(__name__)
GCPs = typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]


def help() -> typing.Tuple[str, str]:
    """"""
    inp = ('    geoloc_spacing\tTODO',
           '    geoloc_row_spacing\tTODO',
           '    geoloc_cell_spacing\tTODO',
           '    geoloc_at_pixel_center\tBoolean set to true if the coordinates'
           ' provided in the input file correspond to the center of the pixels'
           ' and to false if they are referencing the top-left corner of the'
           ' pixels',
           )
    out = ('    gcp_spacing\tTODO',
           '    gcp_row_spacing\tTODO',
           '    gcp_cell_spacing\tTODO',
           '    gcp_distribution\tTODO',
           )
    return ('\n'.join(inp), '\n'.join(out))


def preformat(input_opts: InputOptions, output_opts: OutputOptions,
              granule: Granule
              ) -> typing.Iterator[FormatterResult]:
    """"""
    yield input_opts, output_opts, granule


def _get_distribution_arity(row_count: int, cell_count: int, row_spacing: int,
                            cell_spacing: int) -> typing.Tuple[int, int]:
    """"""
    # Number of subdivisions along each axis
    row_spaces = row_count - 1
    cell_spaces = cell_count - 1

    # Compute the number of GCPs to place along each axis of the geolocation
    # matrix so that the distance in row/cell between two adjacent GCPs is
    # inferior or equal to the requested spacing
    _output_row_spaces = row_spaces / row_spacing
    output_row_spaces = numpy.ceil(_output_row_spaces).astype('int')
    _output_cell_spaces = cell_spaces / cell_spacing
    output_cell_spaces = numpy.ceil(_output_cell_spaces).astype('int')

    # Convert from number of subdivisions to number of row/cell
    output_nrow = output_row_spaces + 1
    output_ncell = output_cell_spaces + 1

    return (output_nrow, output_ncell)


def create_uniform_gcp_distribution(granule: Granule,
                                    input_opts: InputOptions,
                                    output_opts: OutputOptions,
                                    geo_shape: numpy.typing.NDArray
                                    ) -> typing.Dict[str,
                                                     numpy.typing.NDArray]:
    """"""
    full_geoloc_nrow = geo_shape[0]
    full_geoloc_ncell = geo_shape[1]
    data_nrow = granule.dims['row']
    data_ncell = granule.dims['cell']

    # Number of digital points per GCP in the input
    geoloc_spacing = int(input_opts.get('geoloc_spacing', 32))
    geoloc_row_spacing = int(input_opts.get('geoloc_row_spacing',
                                            geoloc_spacing))
    geoloc_cell_spacing = int(input_opts.get('geoloc_cell_spacing',
                                             geoloc_spacing))

    geoloc_nrow, geoloc_ncell = _get_distribution_arity(full_geoloc_nrow,
                                                        full_geoloc_ncell,
                                                        geoloc_row_spacing,
                                                        geoloc_cell_spacing)

    # Compute uniform distribution for geoloc data
    # The max index value (array length - 1) MUST be included in the result
    _geoloc_row = numpy.linspace(0, full_geoloc_nrow - 1, num=geoloc_nrow)
    geoloc_row = numpy.round(_geoloc_row).astype('int')
    _geoloc_cell = numpy.linspace(0, full_geoloc_ncell - 1, num=geoloc_ncell)
    geoloc_cell = numpy.round(_geoloc_cell).astype('int')

    # Number of digital points per GCP in the output
    gcp_spacing = int(output_opts.get('gcp_spacing', 32))
    gcp_row_spacing = int(output_opts.get('gcp_row_spacing',
                                          gcp_spacing))
    gcp_cell_spacing = int(output_opts.get('gcp_cell_spacing',
                                           gcp_spacing))

    # Warn user if requested GCP resolution exceeds geolocation resolution for
    # the row axis
    _native_row_spacing = data_nrow / full_geoloc_nrow
    native_row_spacing = numpy.ceil(_native_row_spacing).astype('int')
    if native_row_spacing > gcp_row_spacing:
        logger.warning('Requested GCP spacing on the row axis is lower than '
                       'geolocation spacing in input data')
        logger.debug(f'Native geoloc row spacing: {native_row_spacing}')
        logger.debug(f'Requested row spacing: {gcp_row_spacing}')

    # Warn user if requested GCP resolution exceeds geolocation resolution for
    # the cell axis
    _native_cell_spacing = data_ncell / full_geoloc_ncell
    native_cell_spacing = numpy.ceil(_native_cell_spacing).astype('int')
    if native_cell_spacing > gcp_cell_spacing:
        logger.warning('Requested GCP spacing on the cell axis is lower than '
                       'geolocation spacing in input data')
        logger.debug(f'Native geoloc cell spacing: {native_cell_spacing}')
        logger.debug(f'Requested cell spacing: {gcp_cell_spacing}')

    # GCPs will be placed automatically on the bottom and right edges of the
    # data matrix at a later stage, so consider that the data matrix is shorter
    # by one requested spacing along each axis
    tmp_nrow = data_nrow - gcp_row_spacing
    tmp_ncell = data_ncell - gcp_cell_spacing

    # Number of output GCPs to place along each direction
    gcp_nrow, gcp_ncell = _get_distribution_arity(tmp_nrow, tmp_ncell,
                                                  gcp_row_spacing,
                                                  gcp_cell_spacing)

    # Compute uniform distribution for output GCPs
    gcp_row = numpy.arange(gcp_nrow) * gcp_row_spacing
    gcp_cell = numpy.arange(gcp_ncell) * gcp_cell_spacing

    # Compute indices in the data matrix that match the extracted geoloc inputs
    row = numpy.linspace(0, data_nrow - 1, num=full_geoloc_nrow)
    cell = numpy.linspace(0, data_ncell - 1, num=full_geoloc_ncell)
    data_row = row[geoloc_row]
    data_cell = cell[geoloc_cell]

    result = {'geoloc_row': geoloc_row, 'geoloc_cell': geoloc_cell,
              'input_row': data_row, 'input_cell': data_cell,
              'output_row': gcp_row, 'output_cell': gcp_cell}

    return result


def compute_gcps(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 granule: Granule) -> GCPs:
    """"""
    nrow = granule.dims['row']
    ncell = granule.dims['cell']

    # Compute GCPs
    lon = granule.vars['lon']['array']
    lat = granule.vars['lat']['array']

    gcp_distribution = output_opts.get('gcp_distribution', None)
    if gcp_distribution is None:
        gcp_distribution = create_uniform_gcp_distribution(granule,
                                                           input_opts,
                                                           output_opts,
                                                           numpy.shape(lon))

    _geoloc_row = gcp_distribution['geoloc_row']
    _geoloc_cell = gcp_distribution['geoloc_cell']
    _input_row = gcp_distribution['input_row']
    _input_cell = gcp_distribution['input_cell']
    _output_row = gcp_distribution['output_row']
    _output_cell = gcp_distribution['output_cell']

    geoloc_nrow = numpy.shape(_geoloc_row)[0]
    geoloc_ncell = numpy.shape(_geoloc_cell)[0]

    # Indices of the data matrix must be reshaped so that numpy can use them
    # to extract the associated values
    let_numpy_guess = -1
    geoloc_row = _geoloc_row.reshape((let_numpy_guess, 1))
    geoloc_cell = _geoloc_cell.reshape((1, let_numpy_guess))

    # Read geographical coordinates of the reference points that will be used
    # compute the GCPs
    src_lon = lon[geoloc_row, geoloc_cell]
    src_lat = lat[geoloc_row, geoloc_cell]

    # GCP pixels are located at the edge of data pixels, meaning that the
    # center of the first data pixel is located at (0.5, 0.5) in the GCPs
    # matrix.
    # If lon/lat correspond to the center of data pixels, then the indices
    # stored in the GCPs must be shifted by one half-pixel along each axis
    _geoloc_at_pixel_center = input_opts.get('geoloc_at_pixel_center', 'true')
    geoloc_at_pixel_center = _geoloc_at_pixel_center.lower() in ('true', 'yes')
    if geoloc_at_pixel_center:
        _input_row = _input_row + 0.5
        _input_cell = _input_cell + 0.5

    # Build a matrix for the row and cell coordinates of the reference points
    # in the data matrix by repeating indices vector along the orthogonal axis
    input_row = _input_row.reshape((let_numpy_guess, 1))
    input_cell = _input_cell.reshape((1, let_numpy_guess))
    input_row = numpy.tile(input_row, (1, geoloc_ncell))
    input_cell = numpy.tile(input_cell, (geoloc_nrow, 1))

    # Indices of resulting GCPs must be integer values
    output_row = numpy.floor(_output_row).astype('int')
    output_cell = numpy.floor(_output_cell).astype('int')

    # Add an extra line and column to geolocate the bottom and right edges of
    # the data matrix
    output_row = numpy.concatenate((output_row, [nrow]))
    output_cell = numpy.concatenate((output_cell, [ncell]))
    ngcps = [output_row.size, output_cell.size]

    # Since the (i, j) of the original GCPs might have been float values, it
    # is necessary to compute the geographical coordinates for the integer
    # version of (i, j)
    _use_gdal = output_opts.get('use_gdal', 'no')
    use_gdal = _use_gdal.lower() in ('true', 'yes')
    if use_gdal is True:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            try:
                from osgeo import gdal  # find a way to remove this
            except ImportError:
                import gdal  # find a way to remove this
        drv = gdal.GetDriverByName('MEM')
        dset = drv.Create('tmp', ncell, nrow)
        gcps = []
        for _lon, _lat, _cell, _row in zip(src_lon.flat, src_lat.flat,
                                           input_cell.flat, input_row.flat):
            out_lon = float(_lon)
            out_lat = float(_lat)
            out_hei = float(0)
            out_cell = float(_cell)
            out_row = float(_row)
            gcps.append(gdal.GCP(out_lon, out_lat, out_hei, out_cell, out_row))
        dset.SetGCPs(gcps, idf_converter.lib.constants.EPSG4326_WKT)
        options = ['MAX_GCP_ORDER=-1']
        transformer = gdal.Transformer(dset, None, options)
        _output_row = numpy.tile(output_row[:, numpy.newaxis], (1, ngcps[1]))
        _output_cell = numpy.tile(output_cell[numpy.newaxis, :], (ngcps[0], 1))

        # Extra/Interpolate geo coordinates for the requested indices
        inputs = numpy.vstack((_output_cell.flatten(),
                               _output_row.flatten())).transpose()
        outputs = numpy.array(transformer.TransformPoints(0, inputs)[0])[:,
                                                                         0:2]
        output_lat = outputs[:, 1].reshape(ngcps)
        output_lon = outputs[:, 0].reshape(ngcps)
        dset = None
    else:
        interp_gcps = idf_converter.lib.interp.geoloc_from_gcps
        _output_row = numpy.tile(output_row[:, numpy.newaxis], (1, ngcps[1]))
        _output_cell = numpy.tile(output_cell[numpy.newaxis, :], (ngcps[0], 1))
        output_lon, output_lat = interp_gcps(src_lon, src_lat,
                                             input_row, input_cell,
                                             _output_row, _output_cell)
        output_lon = _fix_swath_longitudes(output_lon, 9)

    return output_lon, output_lat, output_row, output_cell


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

    input_opts, output_opts, granule = fix_swath_longitudes(input_opts,
                                                            output_opts,
                                                            granule,
                                                            targets=('lon',),
                                                            decimals=9)

    gcp_lon, gcp_lat, gcp_lin, gcp_pix = compute_gcps(input_opts, output_opts,
                                                      granule)
    gcp_nrow, gcp_ncell = gcp_lon.shape

    nrow = granule.dims['row']
    ncell = granule.dims['cell']

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
    idf_file.createDimension('row', nrow)
    idf_file.createDimension('cell', ncell)
    idf_file.createDimension('row_gcp', gcp_nrow)
    idf_file.createDimension('cell_gcp', gcp_ncell)
    idf_dims = ('time', 'row', 'cell', 'row_gcp', 'cell_gcp',)
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

    _latgcp = idf_file.createVariable('lat_gcp', 'f4',
                                      ('row_gcp', 'cell_gcp'))
    _latgcp.long_name = 'ground control points latitude'
    _latgcp.standard_name = 'latitude'
    _latgcp.units = 'degrees_north'
    _latgcp[:] = gcp_lat.astype('float32')

    _longcp = idf_file.createVariable('lon_gcp', 'f4', ('row_gcp', 'cell_gcp'))
    _longcp.long_name = 'ground control points longitude'
    _longcp.standard_name = 'longitude'
    _longcp.units = 'degrees_east'
    _longcp[:] = gcp_lon.astype('float32')

    _indexrowgcp = idf_file.createVariable('index_row_gcp', 'i4', ('row_gcp',))
    _indexrowgcp.long_name = ('index of ground control points in row '
                              'dimension')
    _indexrowgcp.comment = ('index goes from 0 (start of first pixel) to '
                            'dimension value (end of last pixel)')
    _indexrowgcp[:] = gcp_lin.astype('int32')

    _indexcellgcp = idf_file.createVariable('index_cell_gcp', 'i4',
                                            ('cell_gcp',))
    _indexcellgcp.long_name = ('index of ground control points in cell '
                               'dimension')
    _indexcellgcp.comment = ('index goes from 0 (start of first pixel) to '
                             'dimension value (end of last pixel)')
    _indexcellgcp[:] = gcp_pix.astype('int32')

    idf_file.cdm_data_type = b'Swath'

    processed_dims = ['time', 'row', 'cell', 'row_gcp', 'cell_gcp']
    processed_vars = ['time', 'lat_gcp', 'lon_gcp', 'index_row_gcp',
                      'index_cell_gcp', 'lat', 'lon']
    processed_attrs = ['cdm_data_type']

    return (processed_dims, processed_vars, processed_attrs)
