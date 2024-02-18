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

"""This module defines errors related to IDF v.x formatting."""

import typing
import logging
import idf_converter.lib.idf.v1.specs as idf_specs

logger = logging.getLogger(__name__)


class MissingGeolocationProjection(Exception):
    """"""
    def __init__(self) -> None:
        """"""
        msg = ('The geolocation dictionnary must have a value associated with '
               'the "projection" key.')
        super(MissingGeolocationProjection, self).__init__(msg)


class MissingGeolocationDetails(Exception):
    """"""
    def __init__(self) -> None:
        """"""
        msg = ('The geolocation dictionnary must contain either a "gcps" or a '
               '"geotransform" value.')
        super(MissingGeolocationDetails, self).__init__(msg)


class MissingGCPResolution(Exception):
    """"""
    def __init__(self) -> None:
        """"""
        msg = ('You must provide either the  number of GCPs or pixel distance '
               'between GCPs.')
        super(MissingGCPResolution, self).__init__(msg)


class DataModelNotSupported(Exception):
    """"""
    def __init__(self, data_model: str) -> None:
        """"""
        supported_models = idf_specs.SUPPORTED_MODELS.keys()
        msg = ('"{}" not found in the list of supported data models: '
               '{}.'.format(data_model, ', '.join(supported_models)))
        super(DataModelNotSupported, self).__init__(msg)


class MissingData(Exception):
    """"""
    def __init__(self) -> None:
        """"""
        msg = 'The "band" array must contain at least one element'
        super(MissingData, self).__init__(msg)


class MissingMetadata(Exception):
    """"""
    def __init__(self, attribute_names: typing.List[str]) -> None:
        """"""
        msg = ('The following metadata are required but were not provided: '
               '{}.'.format(', '.join(attribute_names)))
        super(MissingMetadata, self).__init__(msg)


class UnknownAttributes(Exception):
    """"""
    def __init__(self, attributes: typing.List[str]) -> None:
        """"""
        extra_str = ', '.join(attributes)
        msg = ('The following attributes are not supported: {}.'
               'If you really want to add them to the global attributes of '
               'the IDF file, please add them to the '
               '"allowed_extra_attributes" parameter'.format(extra_str))
        super(UnknownAttributes, self).__init__(msg)


class MissingVariableMetadata(Exception):
    """"""
    def __init__(self, attributes: typing.Dict[str, typing.List[str]]) -> None:
        """"""
        _msg = ['Some mandatory attributes are missing from the variables '
                'metadata:']
        for band in attributes:
            _msg.append('\t{}: {}'.format(band, ', '.join(attributes[band])))
        msg = '\n'.join(_msg)
        super(MissingVariableMetadata, self).__init__(msg)


class UnknownVariableAttributes(Exception):
    """"""
    def __init__(self, attributes: typing.Dict[str, typing.List[str]]) -> None:
        """"""
        _msg = ['The following variable attributes are not supported:']
        for band in attributes:
            _msg.append('\t{}: {}'.format(band, ', '.join(attributes[band])))
        _msg.append('If you really want them to be included in the IDF file, '
                    'please add them to the allowed_extra_variable_attributes '
                    'parameter.')
        msg = '\n'.join(_msg)
        super(UnknownVariableAttributes, self).__init__(msg)


class InvalidDatetimeType(Exception):
    """"""
    def __init__(self, attr: str) -> None:
        """"""
        msg = ('The "{}" attribute must be a valid datetime.datetime '
               'object.'.format(attr))
        super(InvalidDatetimeType, self).__init__(msg)


class GCPArityInconsistency(Exception):
    """"""
    def __init__(self, sizes: typing.List[int]) -> None:
        """"""
        sizes_str = ['{}'.format(s) for s in sizes]
        msg = ('The inputs provided to generate GCPs must all have the same '
               'size. The provided inputs do not respect this condition as '
               'their sizes are: {}'.format(', '.join(sizes_str)))
        super(GCPArityInconsistency, self).__init__(msg)
