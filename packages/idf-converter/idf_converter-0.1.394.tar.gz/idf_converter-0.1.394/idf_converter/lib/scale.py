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

"""This module provides methods to manipulate the numeric scale and adapt
extrema.
"""

import numpy
import numpy.typing
import typing
import logging
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult, NumValuesDict, Extrema

logger = logging.getLogger(__name__)
MaskGetter = typing.Callable[[Granule, typing.Iterable[str]], NumValuesDict]
ExtremaMethod = typing.Callable[[typing.Dict[str, typing.Any], float, float],
                                Extrema]


def logscale(input_opts: InputOptions,
             output_opts: OutputOptions,
             granule: Granule,
             *args: typing.Iterable[typing.Any],
             base: float,
             targets: typing.Iterable[str]) -> FormatterResult:
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
    base: float
        Base for the logarithm. Natural log will be used if the base passed as
        argument is <= 0.
    targets: tuple
        Identifers for variables that must be converted to logarithmic scale

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the targetted variables
          have been converted to logarithmic scale
    """
    ln_base = 1  # base e
    if 0 < base:
        ln_base = numpy.log(base)

    for var_id in targets:
        lin_values = granule.vars[var_id]['array']
        values_mask = numpy.ma.getmaskarray(lin_values)
        if values_mask.all():
            logger.warning(f'Log scale not applied to {var_id} because all '
                           'values are masked')
            continue
        nan_mask = numpy.isnan(lin_values)
        lin_values[numpy.where(nan_mask)] = 1  # will be overwritten later
        negative_mask = (lin_values <= 0)
        invalid_mask = (negative_mask | values_mask)
        log_values = numpy.log(numpy.ma.getdata(lin_values),
                               where=(~invalid_mask)) / ln_base
        log_values[numpy.where(nan_mask)] = numpy.nan

        log_vmin = numpy.log(granule.vars[var_id]['valid_min']) / ln_base
        log_vmax = numpy.log(granule.vars[var_id]['valid_max']) / ln_base

        # use log(vmin) where values were negative
        log_values[numpy.where(negative_mask)] = log_vmin

        log_values[numpy.where(values_mask)] = numpy.nan

        granule.vars[var_id]['array'] = log_values
        granule.vars[var_id]['valid_min'] = log_vmin
        granule.vars[var_id]['valid_max'] = log_vmax

        if 'units' in granule.vars[var_id].keys():
            _units = granule.vars[var_id]['units']
            if 0 < base:
                granule.vars[var_id]['units'] = f'log{base}({_units})'
            else:
                granule.vars[var_id]['units'] = f'log({_units})'

        comment = ('Logarithm applied to improve contrast and avoid '
                   'sacrificing either small or large scale structures due to '
                   'data storage resolution limitations')
        if 'comment' in granule.vars[var_id].keys():
            _comment = granule.vars[var_id]['comment']
            granule.vars[var_id]['comment'] = f'{_comment}\n{comment}'
        else:
            granule.vars[var_id]['comment'] = comment

    return (input_opts, output_opts, granule)


def stretch_extent(input_opts: InputOptions,
                   output_opts: OutputOptions,
                   granule: Granule,
                   *args: typing.Iterable[typing.Any],
                   targets: typing.Iterable[str],
                   stretch_factor: float,
                   change_vmin: bool,
                   change_vmax: bool) -> FormatterResult:
    """"""
    for var_id in targets:
        vmin = granule.vars[var_id]['valid_min']
        vmax = granule.vars[var_id]['valid_max']

        stretched_extent = stretch_factor * (vmax - vmin)
        if change_vmin == change_vmax:
            mid_value = 0.5 * (vmin + vmax)
            vmin = mid_value - 0.5 * stretched_extent
            vmax = mid_value + 0.5 * stretched_extent
        elif change_vmax:
            vmax = vmin + stretched_extent
        elif change_vmin:
            vmin = vmax - stretched_extent

        granule.vars[var_id]['valid_min'] = vmin
        granule.vars[var_id]['valid_max'] = vmax

    return input_opts, output_opts, granule


def share_extrema(input_opts: InputOptions,
                  output_opts: OutputOptions,
                  granule: Granule,
                  *args: typing.Iterable[typing.Any],
                  targets: typing.List[str]) -> FormatterResult:
    """"""
    vmins = []
    vmaxs = []
    for var_id in targets:
        vmins.append(granule.vars[var_id]['valid_min'])
        vmaxs.append(granule.vars[var_id]['valid_max'])

    shared_min: numpy.typing.ScalarType = numpy.min(vmins)
    shared_max: numpy.typing.ScalarType = numpy.max(vmaxs)
    for var_id in targets:
        granule.vars[var_id]['valid_min'] = shared_min
        granule.vars[var_id]['valid_max'] = shared_max

    return input_opts, output_opts, granule


def contrast_from_pct(input_opts: InputOptions,
                      output_opts: OutputOptions,
                      granule: Granule,
                      *args: typing.Iterable[typing.Any],
                      targets: typing.Iterable[str],
                      valid_threshold: float,
                      common_mask: typing.Optional[numpy.typing.NDArray],
                      bands_mask: typing.Optional[NumValuesDict],
                      dynamic_bands_mask: typing.Optional[MaskGetter],
                      min_percentile: float,
                      max_percentile: float) -> FormatterResult:
    """"""
    dyn_bands_mask: typing.Dict[str, numpy.typing.NDArray] = {}
    if dynamic_bands_mask is not None:
        dyn_bands_mask = dynamic_bands_mask(granule, targets)

    for var_id in targets:
        var_data = granule.vars[var_id]['array']
        invalid_mask = numpy.ma.getmaskarray(var_data)
        if common_mask is not None:
            invalid_mask = (invalid_mask | common_mask)
        if bands_mask is not None and var_id in bands_mask.keys():
            invalid_mask = (invalid_mask | bands_mask[var_id])
        if var_id in dyn_bands_mask.keys():
            invalid_mask = (invalid_mask | dyn_bands_mask[var_id])
        valid_data = numpy.ma.getdata(var_data[numpy.where(~invalid_mask)])
        valid_data_ratio = float(valid_data.size) / float(var_data.data.size)

        # If there are not enough valid data, leave the default min/max
        if valid_data_ratio <= valid_threshold:
            continue

        vmin = numpy.percentile(valid_data, min_percentile)
        vmax = numpy.percentile(valid_data, max_percentile)
        granule.vars[var_id]['valid_min'] = vmin
        granule.vars[var_id]['valid_max'] = vmax
    return input_opts, output_opts, granule


def limit_extrema(input_opts: InputOptions,
                  output_opts: OutputOptions,
                  granule: Granule,
                  *args: typing.Iterable[typing.Any],
                  targets: typing.Iterable[str],
                  min_threshold: typing.Optional[float] = None,
                  max_threshold: typing.Optional[float] = None
                  ) -> FormatterResult:
    """"""
    for var_id in targets:
        if min_threshold is not None:
            var_min = granule.vars[var_id]['valid_min']
            _min = max(var_min, min_threshold)
            granule.vars[var_id]['valid_min'] = _min
        if max_threshold is not None:
            var_max = granule.vars[var_id]['valid_max']
            _max = min(var_max, max_threshold)
            granule.vars[var_id]['valid_max'] = _max
    return input_opts, output_opts, granule


def extrema_methods(input_opts: InputOptions,
                    output_opts: OutputOptions,
                    granule: Granule,
                    *args: typing.Iterable[typing.Any],
                    targets: typing.Iterable[str],
                    methods: typing.Dict[str, ExtremaMethod],
                    min_values: typing.Dict[str, float],
                    max_values: typing.Dict[str, float]) -> FormatterResult:
    """
    Compute custom min/max for each targetted variable. The methods for
    computing the extrema  must accept an entry from the Granule.vars
    dictionary as input, as well as two float values (min and max).

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
        Identifers for variables whose extrema will be modified
    methods: dict
        Dictionary with variable identifiers as keys and methods for computing
        custom extrema as values
    min_values: dict
        Dictionary with variable identifiers as keys and floats as values, to
        be passed as argument for the min value
    max_values: dict
        Dictionary with variable identifiers as keys and floats as values, to
        be passed as argument for the max value

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the targetted variables
          have been masked
    """
    for var_id in targets:
        _min, _max = methods[var_id](granule.vars[var_id],
                                     min_values[var_id],
                                     max_values[var_id])
        granule.vars[var_id]['valid_min'] = _min
        granule.vars[var_id]['valid_max'] = _max

    return input_opts, output_opts, granule
