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

"""This module contains formatter methods for operations related to data
interpolation.
"""

import numpy
import numpy.typing
import pyproj
import typing
import logging
import scipy.interpolate
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


class MissingMandatoryVariable(ValueError):
    """Error raised when at least one variable required by the interpolation
    method is missing from the variables provided as input."""
    pass


class ReferenceVariableMissing(ValueError):
    """Error raised when the variables dictionary does not contain the
    reference variable."""
    def __init__(self, var_name: str) -> None:
        """"""
        msg = (f'Reference variable "{var_name}" not found in the variables '
               'list')
        super(ReferenceVariableMissing, self).__init__(msg)


class CannotInterpolateRefVariable(ValueError):
    """Error raised when a variable is both a target and a reference for the
    interpolation algorithm."""
    def __init__(self, var_id: str) -> None:
        """"""
        self.var_id = var_id


def fill_1d_gaps(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 granule: Granule,
                 *args: typing.Iterable[typing.Any],
                 targets: typing.Iterable[str],
                 reference: str,
                 gaps_indices: numpy.typing.NDArray,
                 method: str,
                 delta: float) -> FormatterResult:
    """
    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.Granule
        Object representing the granule data and metadata
    targets: tuple
        Identifers for variables that must be filled with NaN values where gaps
        have been detected
    reference: str
        Identifier of the variable which has been used to detected gaps
    gaps_indices: numpy.ndarray
        Array indices where gaps have been detected
    method: str
        Interpolation method to use for geographical coordinates
    delta: float
        Sampling expected for the reference variable after interpolation

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the targetted variables
          have been modified to fill the gaps
    """
    var_names = list(granule.vars.keys())
    has_ref = (reference in var_names)
    has_lon = ('lon' in var_names)
    has_lat = ('lat' in var_names)
    if False in (has_ref, has_lon, has_lat,):
        raise MissingMandatoryVariable(has_ref, has_lon, has_lat)

    if reference in targets:
        raise CannotInterpolateRefVariable(reference)

    interpolated: typing.Dict[str, typing.List[numpy.typing.NDArray]] = {}
    interpolated[reference] = []
    interpolated['lon'] = []
    interpolated['lat'] = []

    for var_name in targets:
        interpolated[var_name] = []

    chunk_slice = slice(0, gaps_indices[0] + 1)
    for var_name in var_names:
        var_chunk = granule.vars[var_name]['array'][chunk_slice]
        interpolated[var_name].append(var_chunk)

    ref = granule.vars[reference]['array']
    lon = granule.vars['lon']['array']
    lat = granule.vars['lat']['array']
    func_lon = scipy.interpolate.interp1d(ref, lon, kind=method)
    func_lat = scipy.interpolate.interp1d(ref, lat, kind=method)

    for i in range(len(gaps_indices)):
        ref_start = ref[gaps_indices[i]]
        ref_stop = ref[gaps_indices[i] + 1]
        _intermediary_steps = (ref_stop - ref_start) / delta
        intermediary_steps = numpy.ceil(_intermediary_steps).astype('int')

        # Interpolate lon, lat, time
        _ref_chunk = numpy.linspace(ref_start, ref_stop,
                                    num=2 + intermediary_steps)
        ref_chunk = _ref_chunk[1:-1]  # only keep intermediary steps
        lon_chunk = func_lon(ref_chunk)
        lat_chunk = func_lat(ref_chunk)
        interpolated[reference].append(ref_chunk)
        interpolated['lon'].append(lon_chunk)
        interpolated['lat'].append(lat_chunk)
        chunk_shape = numpy.shape(ref_chunk)

        # add dummy chunks for each variable
        for var_name in targets:
            var_chunk = numpy.full(chunk_shape, numpy.nan)
            interpolated[var_name].append(var_chunk)

        slice_first = gaps_indices[i] + 1
        if i < (len(gaps_indices) - 1):
            slice_last = gaps_indices[i + 1]
            chunk_slice = slice(slice_first, slice_last + 1)
        else:
            chunk_slice = slice(slice_first, None)

        interpolated[reference].append(ref[chunk_slice])
        interpolated['lon'].append(lon[chunk_slice])
        interpolated['lat'].append(lat[chunk_slice])
        for var_name in targets:
            var_chunk = granule.vars[var_name]['array'][chunk_slice]
            interpolated[var_name].append(var_chunk)

    # Concatenate original and interpolated chunks to replace the input data
    concat = numpy.concatenate
    granule.vars[reference]['array'] = concat(interpolated[reference], axis=0)
    granule.vars['lon']['array'] = concat(interpolated['lon'], axis=0)
    granule.vars['lat']['array'] = concat(interpolated['lat'], axis=0)
    for var_name in targets:
        granule.vars[var_name]['array'] = concat(interpolated[var_name],
                                                 axis=0)
    granule.dims[reference] = len(granule.vars[reference]['array'])

    return input_opts, output_opts, granule


def geoloc_from_gcps(gcplon: numpy.typing.NDArray,
                     gcplat: numpy.typing.NDArray,
                     gcplin: numpy.typing.NDArray,
                     gcppix: numpy.typing.NDArray,
                     lin: numpy.typing.NDArray,
                     pix: numpy.typing.NDArray
                     ) -> typing.Tuple[numpy.typing.NDArray,
                                       numpy.typing.NDArray]:
    """"""
    geod = pyproj.Geod(ellps='WGS84')
    fwd, bwd, dis = geod.inv(gcplon[:, :-1], gcplat[:, :-1],
                             gcplon[:, 1:], gcplat[:, 1:])

    # Find line and column for the top-left corner of the 4x4 GCPs cell which
    # contains the requested locations
    nlin, npix = gcplat.shape
    _gcplin = gcplin[:, 0]
    _gcppix = gcppix[0, :]
    top_line: numpy.typing.NDArray
    top_line = numpy.searchsorted(_gcplin, lin, side='right') - 1
    left_column: numpy.typing.NDArray
    left_column = numpy.searchsorted(_gcppix, pix, side='right') - 1

    # Make sure this line and column remain within the matrix and that there
    # are adjacent line and column to define the bottom-right corner of the 4x4
    # GCPs cell
    top_line = numpy.clip(top_line, 0, nlin - 2)
    bottom_line = top_line + 1
    left_column = numpy.clip(left_column, 0, npix - 2)
    right_column = left_column + 1

    # Compute coordinates of the requested locations in the 4x4 GCPs cell
    line_extent = _gcplin[bottom_line] - _gcplin[top_line]
    column_extent = _gcppix[right_column] - _gcppix[left_column]
    line_rel_pos = (lin - _gcplin[top_line]) / line_extent
    column_rel_pos = (pix - _gcppix[left_column]) / column_extent

    # Compute geographical coordinates of the requested locations projected on
    # the top and bottom lines
    lon1, lat1, _ = geod.fwd(gcplon[top_line, left_column],
                             gcplat[top_line, left_column],
                             fwd[top_line, left_column],
                             dis[top_line, left_column] * column_rel_pos)
    lon2, lat2, _ = geod.fwd(gcplon[bottom_line, left_column],
                             gcplat[bottom_line, left_column],
                             fwd[bottom_line, left_column],
                             dis[bottom_line, left_column] * column_rel_pos)

    # Compute the geographical coordinates of the requested locations projected
    # on a virtual column joining the projected points on the top and bottom
    # lines
    fwd12, bwd12, dis12 = geod.inv(lon1, lat1, lon2, lat2)
    lon, lat, _ = geod.fwd(lon1, lat1, fwd12, dis12 * line_rel_pos)

    return lon, lat
