# vim: ts=4:sts=4:sw=4
#
# @date 2020-02-07
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


""""""

import numpy
import typing
import logging
import scipy.ndimage.filters
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)

# Scale factor used to circumvent underflow errors
UFLOW_FIX = 10**6


def s1_radvel_exp(input_opts: InputOptions,
                  output_opts: OutputOptions,
                  granule: Granule,
                  *args: typing.Iterable[typing.Any],
                  targets: typing.Tuple[str],
                  outputs: typing.Tuple[str],
                  incidence_angle: str,
                  sweep_angle: str) -> FormatterResult:
    """"""
    _sweep = granule.vars[sweep_angle]['array']
    _incidence = granule.vars[incidence_angle]['array']
    sinus_incidence = numpy.sin(numpy.deg2rad(_incidence)
                                ).astype(numpy.float64)

    for input_var, output_var in zip(targets, outputs):
        _input = granule.vars[input_var]['array']

        # Descalloping
        corr = (- 20 * _sweep * (abs(_sweep) <= 0.1)
                - 8 * (_sweep + 0.15) * ((_sweep > 0.1) & (_sweep <= 0.54))
                + 50 * (_sweep - 0.65) * (_sweep > 0.54)
                - 8 * (_sweep - 0.15) * ((_sweep < - 0.1) & (_sweep >= - 0.54))
                + 50 * (_sweep + 0.65) * (_sweep < - 0.54))
        corr = corr.astype(numpy.float64) / 106

        # smooth
        smoothed = scipy.ndimage.median_filter(_input + corr, size=(3, 3))

        if output_var not in granule.vars.keys():
            granule.vars[output_var] = {'name': output_var,
                                        'options': {}}

        # Underflow may happen in numpy internal computations when dividing
        # smoothed by sinus_incidence.
        # In this specific case there is not much of a difference between the
        # order of magnitude of the operands, the problem is simply that values
        # are too close to zero, so multiply the numerator and the denominator
        # by the same large number prior to computing the division.
        radvel = (UFLOW_FIX * smoothed) / (UFLOW_FIX * sinus_incidence)
        granule.vars[output_var]['array'] = radvel

        if 'valid_min' not in granule.vars[output_var].keys():
            vmin: numpy.typing.ScalarType
            vmin = numpy.nanmin(granule.vars[output_var]['array'])
            granule.vars[output_var]['valid_min'] = vmin

        if 'valid_max' not in granule.vars[output_var].keys():
            vmax: numpy.typing.ScalarType
            vmax = numpy.nanmax(granule.vars[output_var]['array'])
            granule.vars[output_var]['valid_max'] = vmax

    return (input_opts, output_opts, granule)


def radial_velocity_sign(input_opts: InputOptions,
                         output_opts: OutputOptions,
                         granule: Granule,
                         *args: typing.Iterable[typing.Any],
                         targets: typing.Tuple[str],
                         update_extrema: bool,
                         heading: str) -> FormatterResult:
    """"""
    # Note: assume heading provided in degrees, clockwise from north
    mean_heading = granule.vars[heading]['array'].mean()

    mean_heading_trigo = numpy.deg2rad(90.0 - mean_heading)
    if 0 < numpy.sin(mean_heading_trigo):
        for target in targets:
            _values = granule.vars[target]['array']
            granule.vars[target]['array'] = -1.0 * _values
            if update_extrema is True:
                vmin = granule.vars[target]['valid_min']
                vmax = granule.vars[target]['valid_max']
                granule.vars[target]['valid_min'] = -1.0 * vmax
                granule.vars[target]['valid_max'] = -1.0 * vmin

    return (input_opts, output_opts, granule)
