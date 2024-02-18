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
import scipy.signal
import numpy.typing
import scipy.interpolate
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)

FractionalGrid = typing.Tuple[numpy.ndarray, numpy.ndarray]
Contour = typing.Tuple[numpy.ndarray, numpy.ndarray]


def gen_fractional_grid(param: typing.Dict[str, typing.Any]) -> FractionalGrid:
    """" Generate fractional grid from xml file parameters """
    # retrieve parameters
    elem_n = param['elem_n']  # Across-track
    line_n = param['line_n']  # Along-track
    # Track offset nadir
    toffset_n = param['trackOffset_n']
    # Track offset tie point
    toffset_tx = param['trackOffset_tx']
    # Start offset nadir
    soffset_n = param['startOffset_n']
    # Start offset tie point
    soffset_tx = param['startOffset_tx']
    # Spatial resolution nadir
    res_n = param['res_n']
    # Spatial resolution tie points
    res_tx = param['res_tx']
    # Interpolating tie point fractional grid
    dj_in = numpy.zeros((elem_n), dtype='float')
    di_in = numpy.zeros((line_n), dtype='float')

    # Build fractional grid
    x_tx = toffset_tx * res_tx
    y_tx = soffset_tx * res_n
    start_index = 0
    for j in range(elem_n):
        x_in = (toffset_n - j) * res_n
        dj_in[j] = (x_tx - x_in) / res_tx

    for j in range(start_index, line_n + start_index):
        y_in = (soffset_n + j) * res_n
        di_in[j-start_index] = (y_in - y_tx) / res_n

    return di_in, dj_in


def filter_sst(sst: numpy.typing.NDArray,
               bt8: numpy.typing.NDArray,
               kernel_size: typing.Tuple[int, int]
               ) -> numpy.typing.NDArray:
    filter_kernel: numpy.typing.ArrayLike
    filter_kernel = numpy.ones(kernel_size) / (kernel_size[0] * kernel_size[1])
    sst_diff: numpy.typing.ArrayLike = sst - bt8
    diff_mean = scipy.signal.convolve2d(sst_diff, filter_kernel, mode='same',
                                        boundary='fill', fillvalue=numpy.nan)
    sst_filtered: numpy.typing.NDArray = diff_mean + bt8
    sst_filtered[0, :] = sst[0, :]
    sst_filtered[-1, :] = sst[-1, :]

    return sst_filtered


def get_alongtrack_contour(values: numpy.typing.NDArray,
                           offset: int
                           ) -> Contour:
    """Expects along-track to be the first axis"""
    alongtrack_size = numpy.shape(values)[0]
    idx_i = []
    idx_j = []
    values_mask = numpy.ma.getmaskarray(values)
    for i in range(0, alongtrack_size):
        valid_values = numpy.where(values_mask[i] == False)  # noqa
        if 0 >= numpy.size(valid_values):
            continue
        first: numpy.typing.ScalarType = numpy.min(valid_values[0])
        idx_i.append(i)
        idx_j.append(first)
        for o in range(0, offset):
            idx_i.append(i)
            idx_j.append(first + 1 + o)

        last: numpy.typing.ScalarType = numpy.max(valid_values[0])
        if first != last:
            idx_i.append(i)
            idx_j.append(last)
            for o in range(0, offset):
                idx_i.append(i)
                idx_j.append(min(0, last - (1 + o)))
    result = (numpy.array(idx_i, dtype=int), numpy.array(idx_j, dtype=int))
    return result


def interp_to_grid(coeffs_n2: numpy.typing.NDArray,
                   tcwv: numpy.typing.NDArray,
                   path_tn: numpy.typing.NDArray,
                   di_in: numpy.typing.NDArray,
                   dj_in: numpy.typing.NDArray,
                   elem_n: int,
                   line_n: int
                   ) -> numpy.typing.NDArray:
    """Interpolate TCWV and Pathlength to fractional grid"""
    # Interpolate TCWV
    nrow_metx = numpy.arange((numpy.shape(tcwv)[1]))
    ncol_metx = numpy.arange((numpy.shape(tcwv)[0]))
    interpolator = scipy.interpolate.RegularGridInterpolator
    points = (ncol_metx, nrow_metx)

    # Interpolate TCWV
    func = interpolator(points, tcwv, method='linear',
                        bounds_error=False, fill_value=None)
    _di, _dj = numpy.meshgrid(di_in, dj_in)
    _tcwv = func((_di.ravel(), _dj.ravel()))
    tcwv_in = _tcwv.reshape(elem_n, line_n)  # tcwv at full resolution

    # Interpolate Pathlength
    func = interpolator(points, path_tn, method='nearest',
                        bounds_error=False, fill_value=None)
    _path = func((_di.ravel(), _dj.ravel()))
    path_in = _path.reshape(elem_n, line_n)  # path at full resolution

    # - Interpolate SST coefficients to fractional grid
    coeffs_n2_single = coeffs_n2[:, 0, :, :]
    n2_in = numpy.zeros((elem_n, line_n, 3))
    nrow_n2 = numpy.arange((numpy.shape(coeffs_n2_single)[2]))
    ncol_n2 = numpy.arange((numpy.shape(coeffs_n2_single)[1]))
    points_n2 = (ncol_n2, nrow_n2)
    for index in range(3):
        func = interpolator(points_n2, coeffs_n2_single[index, :, :],
                            method='linear', bounds_error=False,
                            fill_value=None)
        _n2 = func((tcwv_in.ravel(), path_in.ravel()))
        n2_in[:, :, index] = _n2.reshape((elem_n, line_n))
    return n2_in


def n2_sst_from_slstr(input_opts: InputOptions,
                      output_opts: OutputOptions,
                      granule: Granule,
                      *args: typing.Iterable[typing.Any],
                      input_data: typing.Dict[str, typing.Any]
                      ) -> FormatterResult:
    """"""
    view = 'n'  # Nadir view
    tcwv = input_data['tcwv']
    sat_zen_n = input_data['sat_zen_n']
    param = input_data['param']
    coeffs_n2 = input_data['coeffs_n2']
    n11_id = input_data['n11_id']
    n12_id = input_data['n12_id']

    # Copy data to make sure there will be no side effect
    n11 = numpy.ma.copy(granule.vars[n11_id]['array'])
    n12 = numpy.ma.copy(granule.vars[n12_id]['array'])

    # Look for the first column which has a non-masked value
    # Transpose so that the first index corresponds to the first valid
    # longitude (and not the first valid latitude)
    contour_n11 = get_alongtrack_contour(n11, 0)
    n11.mask[contour_n11] = True

    # Convert zenith angles into pathlength
    path_tn = 1.0 / numpy.cos(numpy.deg2rad(sat_zen_n))

    # - Generate fractional grid
    elem_n = param[f'elem_{view}']
    line_n = param[f'line_{view}']
    di_in, dj_in = gen_fractional_grid(param)

    # - Interpolate TCWV and Pathlength to fractional grid
    n2_in = interp_to_grid(coeffs_n2, tcwv, path_tn,
                           di_in, dj_in, elem_n, line_n)

    alpha = n2_in[:, :, 0].transpose()
    beta = n2_in[:, :, 1].transpose()
    gamma = n2_in[:, :, 2].transpose()
    band = (alpha + beta * n12[:, :] + gamma * n11[:, :])
    kernel_size = (3, 3)
    band = filter_sst(band, n11, kernel_size)

    # Remove borders + n to remove pixels affected by the kernel_size kernel
    # n = int((kernel_size[0] - 1) / 2)
    contour_byte = get_alongtrack_contour(n11, 1)
    band[contour_byte] = numpy.nan

    # Delete data copies
    del n11
    del n12

    granule.vars['sst']['array'] = band

    return input_opts, output_opts, granule
