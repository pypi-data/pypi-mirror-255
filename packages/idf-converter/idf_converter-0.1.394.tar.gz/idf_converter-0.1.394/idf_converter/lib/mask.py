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
masking.
"""

import numpy
import numpy.typing
import typing
import logging
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult, NumValuesDict

logger = logging.getLogger(__name__)

MaskMethod = typing.Callable[[typing.Dict[str, typing.Any], str],
                             numpy.ndarray]


def static_common_mask(input_opts: InputOptions,
                       output_opts: OutputOptions,
                       granule: Granule,
                       *args: typing.Iterable[typing.Any],
                       targets: typing.Iterable[str],
                       mask: numpy.typing.NDArray) -> FormatterResult:
    """
    Apply a common mask on one or several variables.

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
        Identifers for variables on which the mask will be applied
    mask: numpy.ndarray
        Array of boolean values used to mask variables. Any cell set to True in
        this array will be masked

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the targetted variables
          have been masked
    """
    masked_ind = numpy.where(mask)
    for var_name in targets:
        granule.vars[var_name]['array'][masked_ind] = numpy.nan

    return input_opts, output_opts, granule


def static_bands_mask(input_opts: InputOptions,
                      output_opts: OutputOptions,
                      granule: Granule,
                      *args: typing.Iterable[typing.Any],
                      targets: typing.Iterable[str],
                      masks: NumValuesDict) -> FormatterResult:
    """
    Apply variable-specific masks.

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
        Identifers for variables on which the mask will be applied
    masks: numpy.ndarray
        Array of boolean values used to mask variables. Any cell set to True in
        this array will be masked

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
        if var_id not in masks.keys():
            continue
        masked_ind = numpy.where(masks[var_id])
        granule.vars[var_id]['array'][masked_ind] = numpy.nan

    return input_opts, output_opts, granule


def mask_methods(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 granule: Granule,
                 *args: typing.Iterable[typing.Any],
                 targets: typing.Iterable[str],
                 methods: typing.Dict[str, MaskMethod]) -> FormatterResult:
    """
    Build and apply a custom mask on each targetted variable. The methods for
    building the mask must accept an entry from the Granule.vars dictionary as
    input.

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
        Identifers for variables on which the mask will be applied
    methods: dict
        Dictionary with variable identifiers as keys and methods for building
        custom masks as values

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
        var_mask = methods[var_id](granule.vars, var_id)
        masked_ind = numpy.where(var_mask)
        granule.vars[var_id]['array'][masked_ind] = numpy.nan

    return input_opts, output_opts, granule


def share_masks(input_opts: InputOptions,
                output_opts: OutputOptions,
                granule: Granule,
                *args: typing.Iterable[typing.Any],
                targets: typing.Iterable[str]) -> FormatterResult:
    """"""
    all_masks = [numpy.ma.getmaskarray(granule.vars[var_id]['array'])
                 for var_id in targets]
    common_mask = numpy.any(all_masks, axis=0)
    for var_id in targets:
        granule.vars[var_id]['array'].mask = common_mask

    return input_opts, output_opts, granule
