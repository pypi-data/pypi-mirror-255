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

"""This module provides methods to filter data matrices.
"""

import typing
import logging
import scipy.signal
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult, NumValuesDict, Extrema

logger = logging.getLogger(__name__)

MaskGetter = typing.Callable[[Granule, typing.List[str]], NumValuesDict]
ExtremaMethod = typing.Callable[[typing.Dict[str, typing.Any], float, float],
                                Extrema]


def median(input_opts: InputOptions,
           output_opts: OutputOptions,
           granule: Granule,
           *args: typing.Iterable[typing.Any],
           targets: typing.Iterable[str],
           kernels: typing.Dict[str, typing.List[int]]) -> FormatterResult:
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
    for var_id in targets:
        if var_id not in kernels:
            continue

        kernel = kernels[var_id]
        var_data = granule.vars[var_id]['array']
        var_data = scipy.signal.medfilt(var_data, kernel_size=kernel)
        granule.vars[var_id]['array'] = var_data
        # (3, 3))

    return (input_opts, output_opts, granule)
