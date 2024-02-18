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

"""This module contains formatter methods for operations related to
geographical coordinates.
"""

import numpy
import numpy.typing
import typing
import logging
from idf_converter.lib import mod360
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


def remove_extra_lon_degrees(input_opts: InputOptions,
                             output_opts: OutputOptions,
                             granule: Granule,
                             *args: typing.Iterable[typing.Any],
                             lon_name: str) -> FormatterResult:
    """
    Shift longitude values to remove extra 360 degrees.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.Granule
        Object representing the granule data and metadata
    lon_name: str
        Identifier for the variable containing longitudes. It has to be passed
        as a keyword argument.

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule)
        A tuple which contains three elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` with the shifted longitudes
    """
    lon = granule.vars[lon_name]['array']
    lon = lon - numpy.floor((numpy.min(lon) + 180.) / 360.) * 360.
    granule.vars[lon_name]['array'] = lon
    return (input_opts, output_opts, granule)


def _fix_swath_longitudes(_lon: numpy.typing.NDArray,
                          decimals: int
                          ) -> numpy.typing.NDArray:
    """"""
    # Start by making sure all values are in [-180.0, 180.0[
    lon, trunc_to_0 = mod360(_lon + 180.0, decimals)
    lon = lon - 180.0

    # Find acrosstrack main direction
    ac0_dlon = lon[0, 1:] - lon[0, :-1]
    ac0_dlon, precision_loss = mod360(ac0_dlon, decimals)
    trunc_to_0 = trunc_to_0 or precision_loss
    ac0_dlon = numpy.mod(ac0_dlon + 180.0, 360.0) - 180.0
    ac0_dlon_trend: numpy.typing.ScalarType = numpy.sum(numpy.sign(ac0_dlon))

    # Make sure that longitude has a monotonic variation along the first
    # row (i.e. "topmost" acrosstrack)
    lon0 = numpy.mod(lon[0, 0] + 180.0, 360.0) - 180.0
    dlon0 = lon[0, :] - lon0
    if 0 < ac0_dlon_trend:
        discordant_ind = numpy.where(dlon0 < 0)
        dlon0[discordant_ind] = numpy.mod(dlon0[discordant_ind] + 360.0, 360.0)
    else:
        discordant_ind = numpy.where(dlon0 > 0)
        dlon0[discordant_ind] = -1.0 * numpy.mod(360.0 - dlon0[discordant_ind],
                                                 360.0)
    lon[0, :] = dlon0 + lon0

    # Adapt each column so that their longitudes are in the same range as
    # values from the first line
    nac = numpy.shape(lon)[1]
    for i in range(0, nac):
        al_lon0 = lon[0, i]
        al_dlon = lon[1:, i] - lon[:-1, i]
        al_dlon, precision_loss = mod360(al_dlon, decimals)
        trunc_to_0 = trunc_to_0 or precision_loss
        al_dlon = numpy.insert(al_dlon, 0, 0.0)
        al_dlon = numpy.mod(al_dlon + 180.0, 360.0) - 180.0
        # TODO (if we find a case where it is necessary): compare sign of
        # ac_dlon with the alongtrack trend
        al_dlon_rel = numpy.cumsum(al_dlon)
        lon[:, i] = al_lon0 + al_dlon_rel

    if trunc_to_0 is True:
        logger.warning('Some angle or longitude values very close to 0 degrees'
                       ' have been truncated to 0 to avoid underflow errors')

    return lon


def fix_swath_longitudes(input_opts: InputOptions,
                         output_opts: OutputOptions,
                         granule: Granule,
                         *args: typing.Iterable[typing.Any],
                         targets: typing.Iterable[str],
                         decimals: int) -> FormatterResult:
    """"""
    _lon = granule.vars['lon']['array']

    lon = _fix_swath_longitudes(_lon, decimals)

    granule.vars['lon']['array'] = lon

    return (input_opts, output_opts, granule)
