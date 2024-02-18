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
from idf_converter.lib.types import ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'GRID_YX'


class MissingVariablesList(Exception):
    """Error raised when the "variables" input option has not been specified by
    the user."""
    pass


class MissingProjection(Exception):
    """Error raised when the "projection" input option has not been specified
    by the user."""
    pass


class MissingSpatialResolution(Exception):
    """Error raised when the "spatial_resolution" input option has not been
    specified by the user."""
    pass


class MissingCoordinatesSystem(Exception):
    """Error raised when the data coordinates system has not been fully defined
    by the user. At least one of the (y_variable, x_variable) and
    (lat_variable, lon_variable) couples must be specified."""
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
           '    x_variable\tIdentifier of the x variable',
           '    y_variable\tIdentifier of the y variable',
           '    x_dimension\tIdentifier of the x dimension'
           ' (defaults to the value of x_variable)',
           '    y_dimension\tIdentifier of the y dimension'
           ' (defaults to the value of y_variable)',
           '    x_reversed\tSet to yes|true|1 if x values should'
           ' be traversed in reverse order (defaults to no|false|0)',
           '    y_reversed\tSet to yes|true|1 if y values should'
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
           '    projection\tDefinition of the projection for the data grid'
           ' (Proj4 format)',
           '    spatial_resolution\tResolution of the grid in meters'
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
           )

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
    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        raise MissingVariablesList()
    var_ids = [x.strip() for x in _var_ids.split(',')]

    proj_def = input_opts.get('projection', None)
    if proj_def is None:
        raise MissingProjection()

    spatial_resolution = input_opts.get('spatial_resolution', None)
    if spatial_resolution is None:
        raise MissingSpatialResolution()

    # Read options related to lat/lon coordinates
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

    # Read options related to y/x coordinates
    x_var_id = input_opts.get('x_variable', None)
    y_var_id = input_opts.get('y_variable', None)
    x_dim_id = input_opts.get('x_dimension', x_var_id)
    y_dim_id = input_opts.get('y_dimension', y_var_id)
    _x_reversed = input_opts.get('x_reversed', False)
    if _x_reversed is not False:
        x_reversed = _x_reversed.lower() in ('yes', 'true', '1')
    else:
        x_reversed = _x_reversed
    _y_reversed = input_opts.get('y_reversed', False)
    if _y_reversed is not False:
        y_reversed = _y_reversed.lower() in ('yes', 'true', '1')
    else:
        y_reversed = _y_reversed

    time_var_id = input_opts.get('time_variable', None)

    # Check that at least one coordinate vars couple is defined
    spatial_coords = None
    if None not in (x_var_id, y_var_id):
        spatial_coords = 'yx'
        dim1_var_id = y_var_id
        dim2_var_id = x_var_id
        dim1_id = y_dim_id
        dim2_id = x_dim_id
        dim1_reversed = y_reversed
        dim2_reversed = x_reversed
    elif None not in (lon_var_id, lat_var_id):
        spatial_coords = 'latlon'
        dim1_var_id = lat_var_id
        dim2_var_id = lon_var_id
        dim1_id = lat_dim_id
        dim2_id = lon_dim_id
        dim1_reversed = lat_reversed
        dim2_reversed = lon_reversed
    else:
        raise MissingCoordinatesSystem()

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
    dim1 = idf_converter.lib.extract_variable_values(f_handler, dim1_var_id,
                                                     False)
    dim2 = idf_converter.lib.extract_variable_values(f_handler, dim2_var_id,
                                                     False)

    dim1_shape = numpy.shape(dim1)
    while (2 < len(dim1_shape)) and 1 == dim1_shape[0]:
        dim1 = dim1[0]
        dim1_shape = numpy.shape(dim1)

    dim2_shape = numpy.shape(dim2)
    while (2 < len(dim2_shape)) and 1 == dim2_shape[0]:
        dim2 = dim2[0]
        dim2_shape = numpy.shape(dim2)

    """
    if 'latlon' == spatial_coords:
        # Handle longitude continuity
        dim2_delta = dim2[1:] - dim2[:-1]
        if 180.0 <= numpy.max(numpy.abs(dim2_delta)):
            lon_neg_ind = numpy.where(dim2 < 0.0)
            dim2[lon_neg_ind] = dim2[lon_neg_ind] + 360.0

        # Wrap data in [-180.0, 180[ instead of [0, 360[
        # This is not a requirement of the IDF specifications but the current
        # implementation of streamlines rendering in SEAScope will not work
        # otherwise
        dim2 = numpy.mod(dim2 + 180.0, 360.0) - 180.0
    """

    # - Depth
    depth_info = idf_converter.lib.generic_grid.get_depth_info(input_opts,
                                                               granule,
                                                               f_handler)

    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)

    dim1_size = f_handler.dimensions[dim1_id].size
    dim2_size = f_handler.dimensions[dim2_id].size

    if 'latlon' == spatial_coords:
        granule.vars['lat'] = {'array': dim1,
                               'units': 'degrees_north',
                               'datatype': dim1.dtype,
                               'options': {}}
        granule.vars['lon'] = {'array': dim2,
                               'units': 'degrees_east',
                               'datatype': dim2.dtype,
                               'options': {}}
    else:
        granule.vars['y'] = {'array': dim1,
                             'datatype': dim1.dtype,
                             'options': {}}
        granule.vars['x'] = {'array': dim2,
                             'datatype': dim2.dtype,
                             'options': {}}
    granule.dims['y'] = dim1_size
    granule.dims['x'] = dim2_size

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = spatial_resolution
    granule.meta['idf_spatial_resolution_units'] = 'm'

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)
    granule.meta['idf_granule_id'] = granule_name

    dim1_info = (dim1_id, dim1_reversed, None, None)
    dim2_info = (dim2_id, dim2_reversed, None, None)

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
