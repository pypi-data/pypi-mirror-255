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
import numpy.typing
import typing
import netCDF4
import logging
import idf_converter.lib
import idf_converter.lib.time
from idf_converter.lib.types import Granule, ReaderResult, IdxSlices, IdxShifts
from idf_converter.lib.types import InputOptions, OutputOptions, TransformsList

logger = logging.getLogger(__name__)

ExtraValues = typing.Dict[str, typing.Dict[str, typing.Any]]
TimeValues = typing.Tuple[typing.Optional[str], typing.Optional[numpy.ndarray]]
DepthInfo = typing.Tuple[typing.Optional[str], slice]
TimeInfo = typing.Tuple[typing.Optional[str], slice]
DimInfo = typing.Tuple[str, bool, typing.Optional[int], typing.Optional[slice]]


class TimeCoverageNotFullyDefined(ValueError):
    """Error raised when the information available in the input file and in
    the input options do not provide enough information to deduce the time
    coverage."""
    pass


class DepthNotFound(Exception):
    """Error raised when the requested depth value is not available in the
    depth variable of the input file."""

    def __init__(self, value: float, tolerance: float) -> None:
        """"""
        self.value = value
        self.tolerance = tolerance


def get_depth_info(input_opts: InputOptions, granule: Granule,
                   idf_handler: netCDF4.Dataset) -> DepthInfo:
    """"""
    depth_dim_id = input_opts.get('depth_dimension', None)
    depth_var_id = input_opts.get('depth_variable', None)

    depth = None
    depth_attrs = {}
    depth_slice = slice(None, None, None)
    if depth_var_id is not None:
        _depth_var = idf_handler.variables[depth_var_id]
        depth = idf_converter.lib.extract_variable_values(idf_handler,
                                                          depth_var_id)
        for attr in _depth_var.ncattrs():
            depth_attrs[attr] = _depth_var.getncattr(attr)

        ndepth = depth.size

        _depth_value = input_opts.get('depth_value', None)
        if _depth_value is not None:
            depth_value = float(_depth_value)
            depth_ind = numpy.where(depth == depth_value)
            if 0 >= len(depth_ind[0]):
                # Look for the closest depth value which sits within the
                # tolerance range
                _depth_tolerance = input_opts.get('depth_tolerance', '0.0')
                depth_tolerance = float(_depth_tolerance)

                closest_ind = numpy.abs(depth - depth_value).argmin()
                closest_value = depth[closest_ind]
                depth_dist = numpy.abs(closest_value - depth_value)

                if depth_tolerance < depth_dist:
                    raise DepthNotFound(depth_value, depth_tolerance)

                depth_value = closest_value
                depth_ind = numpy.where(depth == depth_value)

            depth_slice = slice(depth_ind[0][0], depth_ind[0][0] + 1, None)
            ndepth = 1
            depth = numpy.array([depth_value])

        granule.vars['depth'] = depth_attrs
        granule.vars['depth']['array'] = depth
        granule.vars['depth']['options'] = {}
        granule.dims['depth'] = ndepth

    return (depth_dim_id, depth_slice)


def build_slices(ndims: int,
                 time_axis: int,
                 depth_axis: int,
                 dim1_axis: int,
                 dim2_axis: int,
                 time_slice: typing.Optional[slice],
                 depth_slice: typing.Optional[slice],
                 dim1_slice: typing.Optional[slice],
                 dim2_slice: typing.Optional[slice],
                 dim1_reversed: bool,
                 dim2_reversed: bool
                 ) -> IdxSlices:
    """"""
    # Define slices to extract and implement reverse traversal when
    # necessary
    axis_to_reverse = []
    if dim1_reversed:
        axis_to_reverse.append(dim1_axis)
    if dim2_reversed:
        axis_to_reverse.append(dim2_axis)
    _idx: IdxSlices = [slice(None, None, -1) if i in axis_to_reverse
                       else slice(None, None, None)
                       for i in range(0, ndims)]

    # Override time slice
    if (0 <= time_axis) and (time_slice is not None):
        _idx[time_axis] = time_slice

    # Override depth slice
    if (0 <= depth_axis) and (depth_slice is not None):
        _idx[depth_axis] = depth_slice

    # Override dim1 slice
    if (0 <= dim1_axis) and (dim1_slice is not None):
        _idx[dim1_axis] = dim1_slice

    # Override dim2 slice
    if (0 <= dim2_axis) and (dim2_slice is not None):
        _idx[dim2_axis] = dim2_slice

    return _idx


def get_slices_from_values(var_id: str,
                           extra_values: ExtraValues,
                           time_info: TimeInfo, depth_info: DepthInfo,
                           dim1_info: DimInfo, dim2_info: DimInfo
                           ) -> typing.Tuple[IdxSlices, IdxShifts]:
    """"""
    depth_dim_id, depth_slice = depth_info
    time_dim_id, time_slice = time_info
    dim1_id, dim1_reversed, dim1_shift, dim1_slice = dim1_info
    dim2_id, dim2_reversed, dim2_shift, dim2_slice = dim2_info

    dim1_axis = extra_values[var_id]['dims'].index(dim1_id)
    dim2_axis = extra_values[var_id]['dims'].index(dim2_id)
    depth_axis = -1
    if depth_dim_id is not None:
        if depth_dim_id in extra_values[var_id]['dims']:
            depth_axis = extra_values[var_id]['dims'].index(depth_dim_id)
    time_axis = -1
    if time_dim_id is not None:
        if time_dim_id in extra_values[var_id]['dims']:
            time_axis = extra_values[var_id]['dims'].index(time_dim_id)

    ndims = len(extra_values[var_id]['dims'])

    idx = build_slices(ndims, time_axis, depth_axis, dim1_axis, dim2_axis,
                       time_slice, depth_slice, dim1_slice, dim2_slice,
                       dim1_reversed, dim2_reversed)

    shift_info = {}
    if dim1_shift is not None:
        shift_info[dim1_axis] = dim1_shift
    if dim2_shift is not None:
        shift_info[dim2_axis] = dim2_shift

    return idx, shift_info


def get_slices_from_netcdf(var_id: str, f_handler: netCDF4.Dataset,
                           time_info: TimeInfo, depth_info: DepthInfo,
                           dim1_info: DimInfo, dim2_info: DimInfo
                           ) -> typing.Tuple[IdxSlices, IdxShifts]:
    """"""
    depth_dim_id, depth_slice = depth_info
    time_dim_id, time_slice = time_info
    dim1_id, dim1_reversed, dim1_shift, dim1_slice = dim1_info
    dim2_id, dim2_reversed, dim2_shift, dim2_slice = dim2_info

    netcdf_var = f_handler.variables[var_id]
    dim1_axis: int = netcdf_var.dimensions.index(dim1_id)
    dim2_axis: int = netcdf_var.dimensions.index(dim2_id)
    depth_axis = -1
    if depth_dim_id is not None:
        if depth_dim_id in netcdf_var.dimensions:
            depth_axis = netcdf_var.dimensions.index(depth_dim_id)
    time_axis = -1
    if time_dim_id is not None:
        if time_dim_id in netcdf_var.dimensions:
            time_axis = netcdf_var.dimensions.index(time_dim_id)

    ndims = len(f_handler.variables[var_id].dimensions)

    idx = build_slices(ndims, time_axis, depth_axis, dim1_axis, dim2_axis,
                       time_slice, depth_slice, dim1_slice, dim2_slice,
                       dim1_reversed, dim2_reversed)

    shift_info = {}
    if dim1_shift is not None:
        shift_info[dim1_axis] = dim1_shift
    if dim2_shift is not None:
        shift_info[dim2_axis] = dim2_shift

    return idx, shift_info


def extract_values(granule: Granule, f_handler: netCDF4.Dataset,
                   extra_values: ExtraValues,
                   time_info: DepthInfo, depth_info: DepthInfo,
                   dim1_info: DimInfo,
                   dim2_info: DimInfo,
                   var_id: str) -> None:
    """"""
    depth_dim_id, depth_slice = depth_info
    time_dim_id, time_slice = time_info

    band: numpy.typing.NDArray
    if var_id in extra_values:
        idx, shift_info = get_slices_from_values(var_id, extra_values,
                                                 time_info, depth_info,
                                                 dim1_info, dim2_info)

        # Define basic information about the variable
        var_units = extra_values[var_id].get('units', '')
        granule.vars[var_id] = {'options': {}, 'name': var_id,
                                'units': var_units}

        _idx = tuple(idx)
        if 0 >= len(shift_info):
            band = extra_values[var_id]['array'][_idx]
        else:
            band = extra_values[var_id]['array']
            for axis, amount in shift_info.items():
                band = numpy.roll(band, amount, axis=axis)
            band = band[_idx]
    else:
        idx, shift_info = get_slices_from_netcdf(var_id, f_handler,
                                                 time_info, depth_info,
                                                 dim1_info, dim2_info)

        # Extract as much information as possible from the input variable
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)

        band = idf_converter.lib.extract_variable_values(f_handler, var_id,
                                                         None, idx, shift_info)

    flag_var_id = granule.vars[var_id].get('flag_variable', None)
    if flag_var_id is not None:

        _idx = tuple(idx)

        # Read flag variable
        flag_band: numpy.typing.NDArray
        if flag_var_id in extra_values:
            if 0 >= len(shift_info):
                flag_band = extra_values[flag_var_id]['array'][_idx]
            else:
                flag_band = extra_values[flag_var_id]['array']
                for axis, amount in shift_info.items():
                    flag_band = numpy.roll(flag_band, amount, axis=axis)
                flag_band = flag_band[_idx]
        else:
            if 0 >= len(shift_info):
                flag_band = f_handler.variables[flag_var_id][_idx]
            else:
                flag_band = f_handler.variables[flag_var_id]
                for axis, amount in shift_info.items():
                    flag_band = numpy.roll(flag_band, amount, axis=axis)
                flag_band = flag_band[_idx]

        flag_mask = idf_converter.lib.build_flag_mask(var_id, band, flag_band,
                                                      granule)
        # Update band mask
        band = numpy.ma.masked_where(flag_mask, band)

    if isinstance(band, numpy.ma.MaskedArray):
        granule.vars[var_id]['array'] = band
    else:
        granule.vars[var_id]['array'] = numpy.ma.array(band)

    has_valid_min = 'valid_min' in granule.vars[var_id].keys()
    has_valid_max = 'valid_max' in granule.vars[var_id].keys()
    incomplete_valid_range = False in (has_valid_min, has_valid_max)

    auto_min = (has_valid_min and
                ('auto' == granule.vars[var_id]['valid_min']))
    auto_max = (has_valid_max and
                ('auto' == granule.vars[var_id]['valid_max']))
    has_undefined_extrema = True in (auto_min, auto_max)

    # Compute min/max from values is valid_min/valid_max attributes have
    # not been provided
    band_mask = numpy.ma.getmaskarray(band)
    if band_mask.all():
        logger.warning(f'All values are masked for variable {var_id}')
        if (has_valid_min is False) or auto_min:
            logger.warning('valid_min not specified and no way to guess it '
                           'from input file: please provide it using the '
                           'variable_override mechanism')
        if (has_valid_max is False) or auto_max:
            logger.warning('valid_max not specified and no way to guess it '
                           'from input file: please provide it using the '
                           'variable_override mechanism')
        if incomplete_valid_range or has_undefined_extrema:
            logger.warning(f'Using default [0, 1] valid range for {var_id}')
            granule.vars[var_id]['valid_min'] = band.dtype.type(0)
            granule.vars[var_id]['valid_max'] = band.dtype.type(1)
    else:
        finite_ind = numpy.where(numpy.isfinite(band))
        if (has_valid_min is False) or auto_min:
            granule.vars[var_id]['valid_min'] = numpy.min(band[finite_ind])
        if (has_valid_max is False) or auto_max:
            granule.vars[var_id]['valid_max'] = numpy.max(band[finite_ind])


def single_granule(granule: Granule,
                   f_handler: netCDF4.Dataset,
                   var_ids: typing.List[str],
                   depth_info: DepthInfo,
                   dim1_info: DimInfo,
                   dim2_info: DimInfo,
                   input_opts: InputOptions,
                   output_opts: OutputOptions,
                   time_dim_id: typing.Optional[str],
                   dtimes: numpy.typing.NDArray
                   ) -> typing.Iterator[ReaderResult]:
    """"""
    # Add transforms
    transforms: TransformsList = []

    if 'indicative_time' in input_opts:
        dt_str = input_opts['indicative_time']
        indicative_dt = idf_converter.lib.time.parse_datetime(dt_str)
        dtimes = numpy.array([indicative_dt])

    coverages = idf_converter.lib.time.get_time_coverages(input_opts, granule,
                                                          dtimes)
    if coverages[0] is None:
        logger.error('Impossible to create a granule without a complete '
                     'time coverage')
        raise TimeCoverageNotFullyDefined()

    start_dt, stop_dt = coverages[0]
    if start_dt == stop_dt:
        logger.warning('Time coverage has no duration, i.e. '
                       'time_coverage_start = time_coverage_end')
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    extra_values = input_opts.get('extra_values', {})
    sub_time_info = (time_dim_id, slice(None, None, None))
    for var_id in var_ids:
        extract_values(granule, f_handler, extra_values, sub_time_info,
                       depth_info, dim1_info, dim2_info, var_id)

    output_opts['__export'] = var_ids
    yield (input_opts, output_opts, granule, transforms)


def multi_granule(granule: Granule,
                  f_handler: netCDF4.Dataset,
                  var_ids: typing.List[str],
                  depth_info: DepthInfo,
                  dim1_info: DimInfo,
                  dim2_info: DimInfo,
                  input_opts: InputOptions,
                  output_opts: OutputOptions,
                  time_dim_id: typing.Optional[str],
                  dtimes: numpy.typing.NDArray
                  ) -> typing.Iterator[ReaderResult]:
    """"""
    coverages = idf_converter.lib.time.get_time_coverages(input_opts, granule,
                                                          dtimes)

    extra_values = input_opts.get('extra_values', {})
    for time_ind, dtime in enumerate(dtimes):
        if (dtime is None) or (dtime is numpy.ma.masked):
            logger.warning(f'{time_ind+1}th time is invalid and has been '
                           'skipped')
            continue

        start_dt, stop_dt = coverages[time_ind]
        logger.debug(f'Processing sub-granule {dtime:%Y-%m-%dT%H:%M:%SZ}')

        if (start_dt is None) or (stop_dt is None):
            raise Exception('')  # TODO

        subgranule = idf_converter.lib.create_subgranule(granule,
                                                         output_opts,
                                                         start_dt, stop_dt,
                                                         dtime)
        sub_time_info = (time_dim_id, slice(time_ind, time_ind + 1, None))
        for var_id in granule.vars.keys():
            logger.debug(f'\textracting data for variable {var_id}')
            subgranule.vars[var_id] = {}
            for attr in granule.vars[var_id].keys():
                # Ancillary variables should already have their "array"
                # attribute (lon, lat, etc...) so it will be copied to the
                # subgranule, but other variables should not have this
                # attribute yet
                subgranule.vars[var_id][attr] = granule.vars[var_id][attr]

        for var_id in var_ids:
            extract_values(subgranule, f_handler, extra_values,
                           sub_time_info, depth_info, dim1_info,
                           dim2_info, var_id)

        output_opts['__export'] = var_ids.copy()

        # Add transforms
        transforms: TransformsList = []

        yield (input_opts, output_opts, subgranule, transforms)
