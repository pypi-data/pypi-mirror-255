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

"""This module contains formatter methods for operations related to packing
numerical values.
"""


import typing
import logging

import numpy
import netCDF4

from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


class ParametersRangeMissing(ValueError):
    """Error raised when a variable is missing either the valid_min attribute,
    the valid_max attribute or both.
    """
    def __init__(self, var_name: str) -> None:
        """
        Parameters
        ----------
        var_name: str
            The identifier of the variable which is missing a mandatory
            attribute
        """
        self.var_name = var_name
        msg = (f'Either the "valid_min", "valid_max" or both attributes are '
               f'not defined for variable "{var_name}".')
        super(ParametersRangeMissing, self).__init__(msg)


def as_ubytes(input_opts: InputOptions,
              output_opts: OutputOptions,
              granule: Granule,
              *args: typing.Iterable[typing.Any],
              targets: typing.Iterable[str]) -> FormatterResult:
    """
    Pack numerical values of targetted variables into ubytes and update the
    variables attributes accordingly.

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
        Identifers for variables whose values must be packed as ubytes

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the targetted variables
          have been packed as ubytes
    """
    for var_name in targets:
        has_valid_min = ('valid_min' in granule.vars[var_name].keys())
        has_valid_max = ('valid_max' in granule.vars[var_name].keys())

        if False in (has_valid_min, has_valid_max):
            raise ParametersRangeMissing(var_name)

        values = granule.vars[var_name]['array']
        vmin = granule.vars[var_name]['valid_min']
        vmax = granule.vars[var_name]['valid_max']
        nan_mask = ((numpy.ma.getmaskarray(values)) | (numpy.isnan(values)))

        logger.debug(f'{var_name}: [{vmin}, {vmax}]')

        # Avoid warnings caused by vmin and vmax begin masked values, which
        # may happen when a variable only contains masked values.
        if numpy.ma.is_masked(vmin):
            vmin = 0
        if numpy.ma.is_masked(vmax):
            vmax = 0

        # Converting vmin and vmax to float during scale computation avoids
        # overflow errors
        offset, scale = vmin, (float(vmax) - float(vmin)) / 254.0
        if vmin == vmax:
            scale = 1.0

        unpacked_type = values.dtype.type
        vmin = unpacked_type(vmin)
        vmax = unpacked_type(vmax)
        numpy.clip(values, vmin, vmax, out=values)

        # Required to avoid runtime warnings on masked arrays wherein the
        # division of the _FillValue by the scale cannot be stored by the dtype
        # of the array
        if isinstance(values, numpy.ma.MaskedArray):
            mask = numpy.ma.getmaskarray(values).copy()
            values[numpy.where(mask)] = vmin
            _values = (numpy.ma.getdata(values) - offset) / scale
            values.mask = mask  # Restore mask to avoid side-effects
        else:
            _values = (values - offset) / scale

        # In case the array still contains Nan values, replace them by vmin
        # before calling numpy.round to avoid errors related to type casting
        # (the rounded values corresponding to the NaN will be replaced by 255
        # anyway).
        _values[numpy.where(nan_mask)] = vmin

        result = numpy.round(_values).astype('ubyte')
        result[numpy.where(nan_mask)] = 255

        granule.vars[var_name]['array'] = result
        granule.vars[var_name]['valid_min'] = 0
        granule.vars[var_name]['valid_max'] = 254
        granule.vars[var_name]['scale_factor'] = scale
        granule.vars[var_name]['add_offset'] = offset
        granule.vars[var_name]['_FillValue'] = numpy.ubyte(255)
        granule.vars[var_name]['datatype'] = numpy.ubyte

    return input_opts, output_opts, granule


def as_float32(input_opts: InputOptions,
               output_opts: OutputOptions,
               granule: Granule,
               *args: typing.Iterable[typing.Any],
               targets: typing.Iterable[str]) -> FormatterResult:
    """"""
    fill_value = netCDF4.default_fillvals['f4']
    for var_name in targets:
        has_valid_min = ('valid_min' in granule.vars[var_name].keys())
        has_valid_max = ('valid_max' in granule.vars[var_name].keys())

        if False in (has_valid_min, has_valid_max):
            raise ParametersRangeMissing(var_name)

        values = granule.vars[var_name]['array']
        vmin = granule.vars[var_name]['valid_min']
        vmax = granule.vars[var_name]['valid_max']
        nan_mask = ((numpy.ma.getmaskarray(values)) | (numpy.isnan(values)))

        logger.debug(f'{var_name}: [{vmin}, {vmax}]')

        # Avoid warnings caused by vmin and vmax begin masked values, which
        # may happen when a variable only contains masked values.
        if numpy.ma.is_masked(vmin):
            vmin = 0
        if numpy.ma.is_masked(vmax):
            vmax = 0

        numpy.clip(values, vmin, vmax, out=values)

        result = numpy.ma.getdata(values).astype('float32')
        result[numpy.where(nan_mask)] = fill_value

        granule.vars[var_name]['array'] = result
        granule.vars[var_name]['valid_min'] = numpy.float32(vmin)
        granule.vars[var_name]['valid_max'] = numpy.float32(vmax)
        granule.vars[var_name]['_FillValue'] = fill_value
        granule.vars[var_name]['datatype'] = numpy.float32

    return input_opts, output_opts, granule
