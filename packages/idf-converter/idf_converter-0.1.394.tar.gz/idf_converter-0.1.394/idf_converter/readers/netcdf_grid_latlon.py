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
import netCDF4
import logging
import idf_converter.lib
import idf_converter.lib.time
import idf_converter.lib.generic_grid
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import Granule, ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'GRID_LATLON'


class MissingLongitudeDimension(Exception):
    """Error raised when the "lon_dimension" input option has not been
    specified by the user. If the "lon_variable" has been provided, the reader
    will try this value too, in case the dimension and the variable share the
    same identifier."""
    pass


class MissingLatitudeDimension(Exception):
    """Error raised when the "lat_dimension" input option has not been
    specified by the user. If the "lat_variable" has been provided, the reader
    will try this value too, in case the dimension and the variable share the
    same identifier."""
    pass


class MissingVariablesList(Exception):
    """Error raised when the "variables" input option has not been specified
    by the user."""
    pass


class MissingValidTime(Exception):
    """Error raised when time values are read from a variable in the input
    file but none of them is valid (masked values)."""
    def __init__(self, time_var_id: str) -> None:
        """"""
        self.time_var_id = time_var_id


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           '    variables\tComma-separated list of variable identifiers to'
           ' extract from the input file',
           '    lon_variable\tIdentifier of the longitude variable',
           '    lat_variable\tIdentifier of the latitude variable',
           '    lon_dimension\tIdentifier of the longitude dimension'
           ' (defaults to the value of lon_variable)',
           '    lat_dimension\tIdentifier of the latitude dimension'
           ' (defaults to the value of lat_variable)',
           '    lon_reversed\tSet to yes|true|1 if longitude values should'
           ' be traversed in reverse order (defaults to no|false|0)',
           '    lat_reversed\tSet to yes|true|1 if latitude values should'
           ' be traversed in reverse order (defaults to no|false|0)',
           '    time_variable\tIdentifier of the time variable (optional).'
           ' If time_variable is not defined, then time_coverage_start'
           ' and time_coverage_end attributes must be defined either in the'
           ' input file or via global_overrides',
           '    depth_variable\tIdentifier of the depth variable (optional).'
           ' If depth_variable is defined, it will be assumed that it'
           ' corresponds to the slowest changed dimension after the time '
           ' dimension',
           '    global_overrides\tDefinition of global attributes that are'
           ' either missing or erroneous in the input file. The value of this'
           ' option is a comma-separated list of key:value',
           '    variable_overrides_VAR\tDefinition of variable attributes'
           ' that are either missing or erroneous in the input file.'
           ' VAR is the identifier of the variable and the value of this'
           ' option is a comma-separated list of key:value',
           '    time_coverage_relative_start\tOffset (in seconds) that must'
           ' be applied to the values of the time variable to obtain the lower'
           ' bound of the time coverage. This option is required when there is'
           ' more than one time value in the input file or when it is not'
           ' possible to provide a static value for time_coverage_start and'
           ' time_coverage_end (via input file or global overrides)',
           '    time_coverage_relative_end\tOffset (in seconds) that must'
           ' be applied to the values of the time variable to obtain the upper'
           ' bound of the time coverage. This option is required when there is'
           ' more than one time value in the input file or when it is not'
           ' possible to provide a static value for time_coverage_start and'
           ' time_coverage_end (via input file or global overrides)',
           '    climatology\tdirectory where daily climatology files are'
           ' stored if an anomaly is computed',
           )
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def configure_grid_dimensions(output_opts: OutputOptions,
                              granule: Granule,
                              lat: numpy.typing.NDArray,
                              lat_reversed: bool,
                              lon: numpy.typing.NDArray,
                              lon_reversed: bool
                              ) -> typing.Any:
    """"""
    lat_slice = None
    lat_shift = None
    lon_slice = None
    lon_shift = None

    _remove_oob = output_opts.get('remove_out_of_bounds_coordinates', 'false')
    remove_oob = _remove_oob.lower() in ('yes', 'true', '1')
    if remove_oob is False:
        return (lat, lat_slice, lat_shift, lon, lon_slice, lon_shift)

    # Check that bounds are defined
    _west = granule.meta.get('geospatial_lon_min', None)
    west = None
    if _west is not None:
        try:
            west = float(_west)
            if not numpy.isfinite(west):
                west = None
        except ValueError:
            west = None

    _east = granule.meta.get('geospatial_lon_max', None)
    east = None
    if _east is not None:
        try:
            east = float(_east)
            if not numpy.isfinite(east):
                east = None
        except ValueError:
            east = None

    _south = granule.meta.get('geospatial_lat_min', None)
    south = None
    if _south is not None:
        try:
            south = float(_south)
            if not numpy.isfinite(south):
                south = None
        except ValueError:
            south = None

    _north = granule.meta.get('geospatial_lat_max', None)
    north = None
    if _north is not None:
        try:
            north = float(_north)
            if not numpy.isfinite(north):
                north = None
        except ValueError:
            north = None

    has_lat_bounds = (None not in (south, north))
    has_lon_bounds = (None not in (west, east))
    if (has_lat_bounds or has_lon_bounds) is False:
        # No bounds defined
        return (lat, lat_slice, lat_shift, lon, lon_slice, lon_shift)

    # Compute new slice on latitude dimension
    if has_lat_bounds:
        if lat_reversed:
            lat_slice_start = numpy.where(lat <= north)[0][0]
            _lat_slice_end = numpy.where(lat >= south)[0][-1]
        else:
            lat_slice_start = numpy.where(lat >= south)[0][0]
            _lat_slice_end = numpy.where(lat <= north)[0][-1]

        lat_slice_end = None
        if _lat_slice_end < len(lat) - 1:
            lat_slice_end = _lat_slice_end + 1
        lat_slice = slice(lat_slice_start, lat_slice_end, None)

    # Compute new slice on longitude dimension
    if has_lon_bounds:
        if (east is not None) and (west is not None) and (east < west):
            # Data cross the IDL, shift longitudes so that the IDL is not at
            # the edge of the matrix
            lon_180 = numpy.mod(lon + 180.0, 360.0) - 180.0
            lon_shift = -1 * len(numpy.where(0 > lon_180)[0])
            if lon_reversed:
                lon_shift = -1 * lon_shift

            # Update coordinates to use a world view centered on lon 180.0
            lon_sorted = numpy.roll(lon, lon_shift, axis=0)
            lon = numpy.mod(lon_sorted + 0.0, 360.0) - 0.0
            east = numpy.mod(east + 0.0, 360.0) - 0.0
            west = numpy.mod(west + 0.0, 360.0) - 0.0

        if lon_reversed:
            lon_slice_start = numpy.where(lon <= east)[0][0]
            _lon_slice_end = numpy.where(lon >= west)[0][-1]
        else:
            lon_slice_start = numpy.where(lon >= west)[0][0]
            _lon_slice_end = numpy.where(lon <= east)[0][-1]

        lon_slice_end = None
        if _lon_slice_end < len(lon) - 1:
            lon_slice_end = _lon_slice_end + 1
        lon_slice = slice(lon_slice_start, lon_slice_end, None)

    return (lat, lat_slice, lat_shift, lon, lon_slice, lon_shift)


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
    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        raise MissingVariablesList()
    var_ids = [x.strip() for x in _var_ids.split(',')]

    lon_var_id = input_opts.get('lon_variable', None)
    lat_var_id = input_opts.get('lat_variable', None)
    lon_dim_id = input_opts.get('lon_dimension', lon_var_id)
    lat_dim_id = input_opts.get('lat_dimension', lat_var_id)
    _lon_reversed = input_opts.get('lon_reversed', False)
    if _lon_reversed is not False:
        lon_reversed = _lon_reversed.lower() in ('yes', 'true', '1')
    else:
        lon_reversed = _lon_reversed
    _lat_reversed = input_opts.get('lat_reversed', False)
    if _lat_reversed is not False:
        lat_reversed = _lat_reversed.lower() in ('yes', 'true', '1')
    else:
        lat_reversed = _lat_reversed

    time_var_id = input_opts.get('time_variable', None)

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    idf_converter.lib.apply_global_overrides(input_opts, granule)
    idf_converter.lib.apply_var_overrides(input_opts, granule)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    # Read variables
    f_handler = netCDF4.Dataset(input_path, 'r')
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)

    # - Time
    dtimes: numpy.typing.NDArray = numpy.array([None, ])
    if time_var_id is not None:
        _t = idf_converter.lib.extract_variable_values(f_handler, time_var_id)
        _t_mask = numpy.ma.getmaskarray(_t).copy()
        if _t_mask.all():
            raise MissingValidTime(time_var_id)

        if _t_mask.any():
            logger.warning('Some time values are masked, this is considered '
                           'bad practice. These masked values will be ignored')

            # Temporarily replace masked values by a valid one ortherwise the
            # netCDF4.num2date call will fail. The mask of the time variable
            # will be applied to the output of num2date later on.
            # At this point in the code we know that there is at least one non-
            # masked value, so we use the first we find as a placeholder.
            masked_t_ind = numpy.where(_t_mask)
            first_valid_t = _t[numpy.where(~_t_mask)[0][0]]
            _t[masked_t_ind] = first_valid_t

        _t_units = f_handler.variables[time_var_id].units
        if 'time_units' in input_opts:
            _t_units = input_opts['time_units']
        if 'time_offset' in input_opts:
            _time_offset = float(input_opts['time_offset'])
            _t = _t + _time_offset
        dtimes = netCDF4.num2date(numpy.ma.getdata(_t), _t_units)
        dtimes = idf_converter.lib.time.as_datetimes_array(dtimes)

        # Apply the same mask as the time value read from the input file to
        # ignore cells that were originally masked and were temporarily
        # replaced by valid values to avoid computation issues
        dtimes = numpy.ma.masked_where(_t_mask, dtimes, copy=False)

    # - Space
    _geoloc_at_pixel_center = input_opts.get('geoloc_at_pixel_center',
                                             'true').lower()
    geoloc_at_pixel_center = _geoloc_at_pixel_center in ('true', 'yes', '1')
    if lat_var_id is not None:
        dim1 = idf_converter.lib.extract_variable_values(f_handler, lat_var_id,
                                                         False)
    elif lat_dim_id is not None:
        dim1_max = None
        dim1_min = None
        if hasattr(f_handler, 'northernmost_latitude'):
            dim1_max = float(f_handler.northernmost_latitude)
        elif hasattr(f_handler, 'geospatial_lat_max'):
            dim1_max = float(f_handler.geospatial_lat_max)
        if hasattr(f_handler, 'southernmost_latitude'):
            dim1_min = float(f_handler.southernmost_latitude)
        elif hasattr(f_handler, 'geospatial_lat_min'):
            dim1_min = float(f_handler.geospatial_lat_min)

        if (dim1_min is None) or (dim1_max is None):
            raise MissingLatitudeDimension()

        dim1_size = f_handler.dimensions[lat_dim_id].size
        dlat = (dim1_max - dim1_min) / dim1_size
        _dim1 = [dim1_min + dlat * i for i in range(0, dim1_size)]
        dim1 = numpy.array(_dim1)
        if geoloc_at_pixel_center is True:
            dim1 = dim1 + 0.5 * dlat
    else:
        raise MissingLatitudeDimension()

    if lon_var_id is not None:
        dim2 = idf_converter.lib.extract_variable_values(f_handler, lon_var_id,
                                                         False)
    elif lon_dim_id is not None:
        dim2_max = None
        dim2_min = None
        if hasattr(f_handler, 'easternmost_longitude'):
            dim2_max = float(f_handler.easternmost_longitude)
        elif hasattr(f_handler, 'geospatial_lon_max'):
            dim2_max = float(f_handler.geospatial_lon_max)
        if hasattr(f_handler, 'westernmost_longitude'):
            dim2_min = float(f_handler.westernmost_longitude)
        elif hasattr(f_handler, 'geospatial_lon_min'):
            dim2_min = float(f_handler.geospatial_lon_min)

        if (dim2_min is None) or (dim2_max is None):
            raise MissingLongitudeDimension()

        dim2_size = f_handler.dimensions[lon_dim_id].size
        dlon = (dim2_max - dim2_min) / dim2_size
        _dim2 = [dim2_min + dlon * i for i in range(0, dim2_size)]
        dim2 = numpy.array(_dim2)
        if geoloc_at_pixel_center is True:
            dim2 = dim2 + 0.5 * dlon
    else:
        raise MissingLongitudeDimension()

    dim1_shape = numpy.shape(dim1)
    while (2 < len(dim1_shape)) and 1 == dim1_shape[0]:
        dim1 = dim1[0]
        dim1_shape = numpy.shape(dim1)

    dim2_shape = numpy.shape(dim2)
    while (2 < len(dim2_shape)) and 1 == dim2_shape[0]:
        dim2 = dim2[0]
        dim2_shape = numpy.shape(dim2)

    # The geospatial_lon|lat_min|max attributes have been extracted and set on
    # the granule when calling extract_global_attributes but some files use
    # east|westernmost_longitude and south|northernmost_latitude instead and
    # these attributes are not extracted automatically (not part of IDF v1
    # specs).
    # Global overrides have already been applied, so use these attributes only
    # if the geospatial_lon|lat_min|max attributes are not already set on the
    # granule.
    if 'geospatial_lon_max' not in granule.meta.keys():
        if hasattr(f_handler, 'easternmost_longitude'):
            value = f_handler.easternmost_longitude
            granule.meta['geospatial_lon_max'] = value
    if 'geospatial_lon_min' not in granule.meta.keys():
        if hasattr(f_handler, 'westernmost_longitude'):
            value = f_handler.westernmost_longitude
            granule.meta['geospatial_lon_min'] = value
    if 'geospatial_lat_max' not in granule.meta.keys():
        if hasattr(f_handler, 'northernmost_latitude'):
            value = f_handler.northernmost_latitude
            granule.meta['geospatial_lat_max'] = value
    if 'geospatial_lat_min' not in granule.meta.keys():
        if hasattr(f_handler, 'southernmost_latitude'):
            value = f_handler.southernmost_latitude
            granule.meta['geospatial_lat_min'] = value

    dims_config = configure_grid_dimensions(output_opts, granule,
                                            dim1, lat_reversed,
                                            dim2, lon_reversed)
    dim1, dim1_slice, dim1_shift, dim2, dim2_slice, dim2_shift = dims_config

    if dim1_slice is not None:
        dim1 = dim1[dim1_slice]
    dim1_size = numpy.shape(dim1)[0]

    if dim2_slice is not None:
        dim2 = dim2[dim2_slice]
    dim2_size = numpy.shape(dim2)[0]

    dim1_info = (lat_dim_id, lat_reversed, dim1_shift, dim1_slice)
    dim2_info = (lon_dim_id, lon_reversed, dim2_shift, dim2_slice)

    """
    # Wrap data in [-180.0, 180[ instead of [0, 360[
    # This is not a requirement of the IDF specifications but the current
    # implementation of streamlines rendering in SEAScope will not work
    # otherwise
    wrap_lon_180 = input_opts.get('wrap_lon_180', 'true').lower()
    if wrap_lon_180 in ('true', 'yes', '1'):
        dim2 = numpy.mod(dim2 + 180.0, 360.0) - 180.0
        negative_lon_ind = numpy.where(dim2 < 0)[0]
        if negative_lon_ind.any():
            lon_shift = -negative_lon_ind[0]
        dim2 = numpy.roll(dim2, lon_shift)
    """

    # - Depth
    depth_info = idf_converter.lib.generic_grid.get_depth_info(input_opts,
                                                               granule,
                                                               f_handler)

    granule.vars['lat'] = {'array': dim1,
                           'units': 'degrees_north',
                           'datatype': dim1.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': dim2,
                           'units': 'degrees_east',
                           'datatype': dim2.dtype,
                           'options': {}}
    granule.dims['lat'] = dim1_size
    granule.dims['lon'] = dim2_size

    dlon = dim2[1] - dim2[0]
    dlat = dim1[1] - dim1[0]
    spatial_resolution = min([abs(dlat), abs(dlon)]) * 111000.

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_resolution
    granule.meta['idf_spatial_resolution_units'] = 'm'

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)
    granule.meta['idf_granule_id'] = granule_name

    if 'indicative_times' in input_opts:
        dtimes = input_opts['indicative_times']
    generic_processor = idf_converter.lib.generic_grid.single_granule
    if 1 < len(dtimes):
        generic_processor = idf_converter.lib.generic_grid.multi_granule
    for extracted_data in generic_processor(granule, f_handler, var_ids,
                                            depth_info, dim1_info, dim2_info,
                                            input_opts, output_opts,
                                            time_var_id, dtimes):
        yield extracted_data

    f_handler.close()
