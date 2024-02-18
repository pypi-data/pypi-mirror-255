# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-13
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
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


class MissingVariableForRemoval(ValueError):
    """Error raised when a variable which has been listed as a target for
    removal is not available in the granule. Although the result is the same
    (i.e. the variable is not in the granule at the end of the operation), this
    should not happen."""
    def __init__(self, var_id: str) -> None:
        """"""
        self.var_id = var_id


def remove_vars(input_opts: InputOptions,
                output_opts: OutputOptions,
                granule: Granule,
                *args: typing.Iterable[typing.Any],
                targets: typing.Iterable[str]) -> FormatterResult:
    """"""
    for target in targets:
        _ = granule.vars.pop(target, None)
        if _ is None:
            raise MissingVariableForRemoval(target)

    output_opts['__export'] = [_ for _ in output_opts['__export']
                               if _ not in targets]
    return input_opts, output_opts, granule
