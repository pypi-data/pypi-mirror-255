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

import typing
import logging

import numpy
import numpy.typing

from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


class UnknownPolarisation(Exception):
    def __init__(self, pol: str):
        self.polarisation = pol


def cmodhh(u10: numpy.typing.NDArray,
           phi: numpy.typing.NDArray,
           inc: numpy.typing.NDArray
           ) -> numpy.typing.NDArray:
    """
    """
    # Zhang Biao, Mouche Alexis, Lu Yiru, Perrie William, Zhang Guosheng,
    # Wang He (2019).
    # A Geophysical Model Function for Wind Speed Retrieval from C-Band
    # HH-polarized Synthetic Aperture Radar.
    # Ieee Geoscience And Remote Sensing Letters, 16(10), 1521-1525.
    # Publisher's official version : https://doi.org/10.1109/LGRS.2019.2905578
    # Open Access version : https://archimer.ifremer.fr/doc/00485/59715/

    # Coefficients and constants
    c = [
        0.,  # fake coeff in order to start with c[1]
        -0.72722756511, -1.1901195406, 0.33968637656, 0.086759069544,
        0.003090124916, 0.011761378188, 0.129158495658, 0.083506931034,
        4.092557781322, 1.211169044551, -1.119776245438, 0.579066509504,
        -0.604527699539, 0.118371042255, 0.008955505675, 0.219608674529,
        0.017557536680, 24.442309754388, 1.983490330585, 6.781440647278,
        7.947947040974, -4.696499003167, -0.437054238710, 5.471252046908,
        0.639468224273, 0.673385731705, 3.433229044819, 0.367036215316
    ]
    zpow = 1.6
    thetm = 40.
    thethr = 25.
    y0 = c[19]
    pn = c[20]
    a = y0 - (y0 - 1.) / pn
    b = 1. / (pn * (y0 - 1.) ** (pn - 1.))

    # Angles
    cosphi = numpy.cos(numpy.deg2rad(phi))
    x = (inc - thetm) / thethr
    x2 = x ** 2.

    # B0 term
    a0 = c[1] + c[2] * x + c[3] * x2 + c[4] * x * x2
    a1 = c[5] + c[6] * x
    a2 = c[7] + c[8] * x
    gam = c[9] + c[10] * x + c[11] * x2
    s0 = c[12] + c[13] * x
    s = a2 * u10
    del a2
    a3 = 1. / (1. + numpy.exp(-s0))
    slts0 = s < s0
    a3[~slts0] = 1. / (1. + numpy.exp(-s[~slts0]))
    a3_pow = (s0[slts0] * (1. - a3[slts0]))
    a3[slts0] = a3[slts0] * (s[slts0] / s0[slts0]) ** a3_pow
    del a3_pow
    del s
    del s0
    del slts0
    b0 = (a3 ** gam) * 10. ** (a0 + a1 * u10)
    del gam
    del a0
    del a1
    del a3

    # B1 term
    b1 = c[15] * u10 * (0.5 + x - numpy.tanh(4. * (x + c[16] + c[17] * u10)))
    b1 = (c[14] * (1. + x) - b1) / (numpy.exp(0.34 * (u10 - c[18])) + 1.)

    # B2 term
    v0 = c[21] + c[22] * x + c[23] * x2
    d1 = c[24] + c[25] * x + c[26] * x2
    d2 = c[27] + c[28] * x
    del x
    del x2
    v2 = (u10 / v0 + 1.)
    del v0
    v2lty0 = v2 < y0
    v2[v2lty0] = a + b * (v2[v2lty0] - 1.) ** pn
    b2 = (-d1 + d2 * v2) * numpy.exp(-v2)
    del d1
    del d2
    del v2

    # Sigma0 according to Fourier terms
    sig = (b0 * (1. + b1 * cosphi + b2 * (2. * cosphi ** 2. - 1.))) ** zpow
    del b0
    del b1
    del b2
    del cosphi
    return sig


def cmod5(u10: numpy.typing.NDArray,
          phi: numpy.typing.NDArray,
          inc: numpy.typing.NDArray,
          neutral: bool = True
          ) -> numpy.typing.NDArray:
    """
    """
    # Coefficients and constants
    if neutral is True:  # CMOD5.n coefficients
        c = [0., -0.6878, -0.7957, 0.338, -0.1728, 0., 0.004, 0.1103,
             0.0159, 6.7329, 2.7713, -2.2885, 0.4971, -0.725, 0.045, 0.0066,
             0.3222, 0.012, 22.7, 2.0813, 3., 8.3659, -3.3428, 1.3236,
             6.2437, 2.3893, 0.3249, 4.159, 1.693]
    else:  # CMOD5 coefficients
        c = [0., -0.688, -0.793, 0.338, -0.173, 0., 0.004, 0.111,
             0.0162, 6.34, 2.57, -2.18, 0.4, -0.6, 0.045, 0.007,
             0.33, 0.012, 22., 1.95, 3., 8.39, -3.44, 1.36, 5.35,
             1.99, 0.29, 3.80, 1.53]
    zpow = 1.6
    thetm = 40.
    thethr = 25.
    y0 = c[19]
    pn = c[20]
    a = y0 - (y0 - 1.) / pn
    b = 1. / (pn * (y0 - 1.) ** (pn - 1.))

    # Angles
    cosphi = numpy.cos(numpy.deg2rad(phi))
    x = (inc - thetm) / thethr
    x2 = x ** 2.

    # B0 term
    a0 = c[1] + c[2] * x + c[3] * x2 + c[4] * x * x2
    a1 = c[5] + c[6] * x
    a2 = c[7] + c[8] * x
    gam = c[9] + c[10] * x + c[11] * x2
    s0 = c[12] + c[13] * x
    s = a2 * u10
    del a2
    a3 = 1. / (1. + numpy.exp(-s0))
    slts0 = s < s0
    a3[~slts0] = 1. / (1. + numpy.exp(-s[~slts0]))
    a3_pow = (s0[slts0] * (1. - a3[slts0]))
    a3[slts0] = a3[slts0] * (s[slts0] / s0[slts0]) ** a3_pow
    del a3_pow
    del s
    del s0
    del slts0
    b0 = (a3 ** gam) * 10. ** (a0 + a1 * u10)
    del gam
    del a0
    del a1
    del a3

    # B1 term
    b1 = c[15] * u10 * (0.5 + x - numpy.tanh(4. * (x + c[16] + c[17] * u10)))
    b1 = (c[14] * (1. + x) - b1) / (numpy.exp(0.34 * (u10 - c[18])) + 1.)

    # B2 term
    v0 = c[21] + c[22] * x + c[23] * x2
    d1 = c[24] + c[25] * x + c[26] * x2
    d2 = c[27] + c[28] * x
    del x
    del x2
    v2 = (u10 / v0 + 1.)
    del v0
    v2lty0 = v2 < y0
    v2[v2lty0] = a + b * (v2[v2lty0] - 1.) ** pn
    b2 = (-d1 + d2 * v2) * numpy.exp(-v2)
    del d1
    del d2
    del v2

    # Sigma0 according to Fourier terms
    sig = b0 * (1. + b1 * cosphi + b2 * (2. * cosphi ** 2. - 1.)) ** zpow
    del b0
    del b1
    del b2
    del cosphi
    return sig


def _compute_roughness(sigma0: numpy.typing.NDArray,
                       incidence: numpy.typing.NDArray,
                       polarisation: str
                       ) -> numpy.typing.NDArray:
    """Compute sea surface roughness.

    Parameters
    ----------
    sigma0 : ndarray
        NRCS backscatter.
    incidence : ndarray
        Incidence angle in degrees.
    polarisation : str
        'VV' or 'HH' or 'VH' or 'HV'

    Returns
    -------
    ndarray
    """
    if polarisation == 'VV':  # Use cmod5
        sigma0_vv = cmod5(10., 45., incidence)
        return sigma0 / sigma0_vv
    elif polarisation == 'HH':  # Use cmodhh
        sigma0_hh = cmodhh(10., 45., incidence)
        return sigma0 / sigma0_hh
    elif polarisation == 'VH' or polarisation == 'HV':  # Use simple model
        # nrcs_vh_db = 0.580*wsp - 35.652
        # nrcs_vh_lin = 10^(nrcs_vh_db/10.)
        sigma0_cross = 10 ** ((0.58 * 10. - 35.652) / 10.)
        return sigma0 / sigma0_cross
    else:
        raise UnknownPolarisation(polarisation)


def compute_roughness(input_opts: InputOptions,
                      output_opts: OutputOptions,
                      granule: Granule,
                      *args: typing.Iterable[typing.Any],
                      targets: typing.Sequence[str],
                      sigma0_var_id: str,
                      incidence_var_id: str,
                      polarisation: str) -> FormatterResult:
    """"""
    # Inputs
    sigma0 = granule.vars[sigma0_var_id]['array']
    incidence = granule.vars[incidence_var_id]['array']
    # Roughness calculation
    # By blocks in order to decrease memory usage
    naz, nra = sigma0.shape
    roughness = numpy.empty((naz, nra), dtype='float32')
    blocksize = 25000000
    block_nra = nra
    block_naz = numpy.maximum(blocksize // block_nra, 1)
    nblock = int(numpy.ceil(naz / float(block_naz)))
    for iblock in range(nblock):
        az0 = iblock * block_naz
        az1 = numpy.minimum((iblock + 1) * block_naz, naz)
        az_slice = slice(az0, az1)
        _roughness = _compute_roughness(sigma0[az_slice, :],
                                        incidence[az_slice, :],
                                        polarisation)
        roughness[az_slice, :] = numpy.sqrt(_roughness)
    granule.vars[targets[0]]['array'] = roughness

    return input_opts, output_opts, granule
