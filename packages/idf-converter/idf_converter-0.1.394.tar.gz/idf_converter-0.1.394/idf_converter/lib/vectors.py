# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-09
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
from idf_converter.lib import mod2pi
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)

DirConfig = typing.Dict[str, typing.Dict[str, typing.Any]]


class MissingVectorConfig(ValueError):
    """Error raised when it is not possible to compute one of the requested
    vectors because its configuration has not been provided."""
    def __init__(self, name: str) -> None:
        self.name = name


class MissingDirectionVariable(ValueError):
    """Error raised when the vector configuration does not define the name of
    the variable which contains direction data."""
    pass


class MissingDirectionData(Exception):
    """Error raised when the variable for the vector direction is not
    available in the granule."""
    def __init__(self, var_name: str) -> None:
        """"""
        self.var_name = var_name


class MissingModuleData(Exception):
    """Error raised when the variable for the vector module is not available
    in the granule."""
    def __init__(self, var_name: str) -> None:
        """"""
        self.var_name = var_name


def from_dir(input_opts: InputOptions,
             output_opts: OutputOptions,
             granule: Granule,
             *args: typing.Iterable[typing.Any],
             targets: typing.Iterable[str],
             configs: DirConfig) -> FormatterResult:
    """"""
    for target in targets:
        cfg = configs.get(target, None)
        if cfg is None:
            raise MissingVectorConfig(target)

        direction_var_name = cfg.get('direction', None)
        if direction_var_name is None:
            raise MissingDirectionVariable()

        has_extra_values = 'extra_values' in input_opts.keys()

        if direction_var_name in granule.vars.keys():
            dir_data = granule.vars[direction_var_name]['array']
        elif has_extra_values:
            if direction_var_name in input_opts['extra_values'].keys():
                dir_var = input_opts['extra_values'][direction_var_name]
                dir_data = dir_var['array']
            else:
                raise MissingDirectionData(direction_var_name)
        else:
            raise MissingDirectionData(direction_var_name)

        units = None
        module_data = None
        module_var_name = cfg.get('module', None)
        if module_var_name is not None:
            if module_var_name in granule.vars.keys():
                units = granule.vars[module_var_name].get('units', '')
                module_data = granule.vars[module_var_name]['array']
            elif has_extra_values:
                if module_var_name in input_opts['extra_values'].keys():
                    module_var = input_opts['extra_values'][module_var_name]
                    units = module_var.get('units', '')
                    module_data = module_var['array']
                else:
                    raise MissingModuleData(module_var_name)
            else:
                raise MissingModuleData(module_var_name)
        else:
            units = ''
            module_data = numpy.ones(numpy.shape(dir_data))

        radians = cfg.get('radians', False)
        if not radians:
            dir_data = numpy.deg2rad(dir_data)

        is_meteo_convention = cfg.get('meteo', False)
        if is_meteo_convention:
            # Convert "direction from" to "direction to"
            dir_data, trunc_to_0 = mod2pi(numpy.pi + dir_data, 9)
            if trunc_to_0 is True:
                logger.warning('Some vector angle values very close to 0 have '
                               'been truncated to 0 to avoid underflow issues')

        # Convert to counter-clockwise from east
        angle_to_east = cfg.get('angle_to_east', 0.0)
        rotation_sign = -1.0 if cfg.get('clockwise', False) else 1.0
        _dir_data = angle_to_east + rotation_sign * dir_data
        try:
            dir_data = numpy.mod(_dir_data, 2.0 * numpy.pi,
                                 where=numpy.isfinite(_dir_data))
        except FloatingPointError:
            UFLOW_FIX = 10**6
            dir_data = numpy.mod(UFLOW_FIX * _dir_data,
                                 UFLOW_FIX * 2.0 * numpy.pi,
                                 where=numpy.isfinite(_dir_data))
            eps = numpy.finfo(dir_data.dtype).eps
            underflow_mask = ((dir_data > 0.0) & (dir_data < UFLOW_FIX * eps))
            if underflow_mask.any():
                logger.warning(f'Some direction angles lower than {eps}'
                               ' radians have been truncated to 0 to avoid'
                               ' underflow errors')
                dir_data[numpy.where(underflow_mask)] = 0.0
            dir_data = dir_data / UFLOW_FIX

        try:
            eastward_data = module_data * numpy.cos(dir_data)
        except FloatingPointError:
            module_data_sq = module_data * module_data
            dir_data_sin = numpy.sin(dir_data)
            module_data_sin_sq = module_data_sq * dir_data_sin * dir_data_sin
            sign = numpy.ones(dir_data.shape)
            negative_mask_min = (dir_data > numpy.pi / 2.0)
            negative_mask_max = (dir_data < 3.0 * numpy.pi / 2.0)
            sign[numpy.where(negative_mask_min & negative_mask_max)] = -1.0
            eastward_module = numpy.sqrt(module_data_sq - module_data_sin_sq)
            eastward_data = sign * eastward_module

        try:
            northward_data = module_data * numpy.sin(dir_data)
        except FloatingPointError:
            module_data_sq = module_data * module_data
            dir_data_cos = numpy.cos(dir_data)
            module_data_cos_sq = module_data_sq * dir_data_cos * dir_data_cos
            sign = numpy.ones(dir_data.shape)
            sign[numpy.where(numpy.pi < dir_data)] = -1.0
            northward_module = numpy.sqrt(module_data_sq - module_data_cos_sq)
            northward_data = sign * northward_module

        vmax = numpy.abs(numpy.nanmax(module_data))
        vmin = -1.0 * vmax

        eastward_var_name = f'eastward_{target}'
        granule.vars[eastward_var_name] = {'array': eastward_data,
                                           'name': eastward_var_name,
                                           'units': units,
                                           'valid_min': vmin,
                                           'valid_max': vmax,
                                           'datatype': eastward_data.dtype,
                                           'options': {}}
        northward_var_name = f'northward_{target}'
        granule.vars[northward_var_name] = {'array': northward_data,
                                            'name': northward_var_name,
                                            'units': units,
                                            'valid_min': vmin,
                                            'valid_max': vmax,
                                            'datatype': northward_data.dtype,
                                            'options': {}}

    return input_opts, output_opts, granule
