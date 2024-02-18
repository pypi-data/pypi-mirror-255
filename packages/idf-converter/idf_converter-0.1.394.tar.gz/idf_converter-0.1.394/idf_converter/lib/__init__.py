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

"""This module defines the in-memory representation for granules as well as
helper methods to get submodules for a specific version of the IDF format.
"""

import copy
import numpy
import typing
import logging
import netCDF4
import datetime
import numpy.typing
import idf_converter.lib.time
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import TransformsList, IdxSlices, IdxShifts

logger = logging.getLogger(__name__)


class EarlyExit(Exception):
    """Exception raised when the converter should exit before producing any IDF
    file (e.g. no valid data found in input file)."""
    pass


class IDFVersionNotSupported(ValueError):
    """Error raised when the IDF specifications are requested for an unknown
    version of the format."""
    def __init__(self, version: str) -> None:
        """"""
        self.version = version


class InvalidTimeCoverageOverride(ValueError):
    """Error raised when the global override for one of the time coverage
    bounds is provided in a format that the parsing method does not support."""
    def __init__(self, attr_name: str, attr_value: str) -> None:
        """"""
        self.attr_name = attr_name
        self.attr_value = attr_value


class MissingProcessingLevel(ValueError):
    """Error raised when neither the input file nor the input option contain
    the "processing_level" property which is required to build the granule
    identifier in case the input file contains several times."""
    pass


class MissingProductVersion(ValueError):
    """Error raised when neither the input file nor the input option contain
    the "product_version" property which is required to build the granule
    identifier in case the input file contains several times."""
    pass


class MissingFileVersion(ValueError):
    """Error raised when neither the input file nor the input option contain
    the "file_version" property which is required to build the granule
    identifier in case the input file contains several times."""
    pass


class MissingVirtualVariableTransformName(Exception):
    """Error raised when the name of the transform that will produce a virtual
    variable is not specified in the output options (with the "using" key)."""
    def __init__(self, virtual_var_id: str) -> None:
        """"""
        self.virtual_var_id = virtual_var_id


def get_idf_specs(version: str) -> typing.Any:
    """Get the specifications submodule for a specific version of the IDF
    format.

    Parameters
    ----------
    version: str
        Targetted IDF format version

    Returns
    -------
    module
        A module providing specifications for the requested IDF format version
    """
    if version in ('1.0',):
        import idf_converter.lib.idf.v1.specs
        return idf_converter.lib.idf.v1.specs
    raise IDFVersionNotSupported(version)


def get_idf_formatter(version: str) -> typing.Any:
    """Get the formatter submodule for a specific version of the IDF format.

    Parameters
    ----------
    version: str
        Targetted IDF format version

    Returns
    -------
    module
        A module providing formatting method for the requested IDF format
        version
    """
    if version in ('1.0',):
        import idf_converter.lib.idf.v1.fmt
        return idf_converter.lib.idf.v1.fmt
    raise IDFVersionNotSupported(version)


def create_granule(idf_version: str, data_model: str) -> Granule:
    """"""
    specs = get_idf_specs(idf_version)
    _data_model = data_model.lower()
    dimensions = [x for x in specs.SUPPORTED_MODELS[_data_model][:-2]
                  if x is not None]

    granule = Granule(idf_version, data_model, dimensions)
    return granule


def create_subgranule(original: Granule, output_opts: OutputOptions,
                      start_dt: datetime.datetime, stop_dt: datetime.datetime,
                      dtime: datetime.datetime) -> Granule:
    """"""
    collection = output_opts.get('collection')
    processing_level = original.meta.get('processing_level', None)
    if processing_level is None:
        logger.error('Missing "processing_level" global attribute')
        raise MissingProcessingLevel()
    product_version = original.meta.get('product_version', None)
    if product_version is None:
        logger.error('Missing "product_version" global attribute')
        raise MissingProductVersion()
    file_version = original.meta.get('file_version', None)
    if file_version is None:
        logger.error('Missing "file_version" global attribute')
        raise MissingFileVersion()

    # <ProductString>_<YYYYMMDD><HHMMSS>_<ProcessingLevel>_v<ProductVersion>_fv<FileVersion>  # noqa
    indicative_datetime = f'{dtime:%Y%m%d%H%M%S}'
    granule_name = f'{collection}_{indicative_datetime}'
    granule_name = f'{granule_name}_{processing_level}'
    granule_name = f'{granule_name}_v{product_version}'
    granule_name = f'{granule_name}_fv{file_version}'

    subgranule: Granule = create_granule(original.idf_version,
                                         original.data_model)
    subgranule.meta = copy.deepcopy(original.meta)

    subgranule.dims = copy.deepcopy(original.dims)

    subgranule.meta['idf_granule_id'] = granule_name
    subgranule.meta['time_coverage_start'] = start_dt
    subgranule.meta['time_coverage_end'] = stop_dt

    return subgranule


def extract_global_attributes(f_handler: netCDF4.Dataset,
                              input_opts: InputOptions,
                              granule: Granule) -> None:
    """"""
    _parse_datetime = idf_converter.lib.time.parse_datetime
    specs = get_idf_specs(granule.idf_version)
    for attr_name in specs.MANDATORY_ATTRIBUTES:
        if attr_name in granule.meta.keys():
            continue
        if hasattr(f_handler, attr_name):
            attr_value = getattr(f_handler, attr_name)
            is_time_coverage_attr = (attr_name in ('time_coverage_start',
                                                   'time_coverage_end'))
            if is_time_coverage_attr and isinstance(attr_value, str):
                suffix_attr = f'{attr_name}_suffix'
                suffix = input_opts.get(suffix_attr, '')
                attr_value = f'{attr_value}{suffix}'
                time_coverage_fmt = input_opts.get('time_coverage_format',
                                                   None)
                try:
                    attr_value = _parse_datetime(attr_value, time_coverage_fmt)
                except idf_converter.lib.time.InvalidDatetimeFormat:
                    logger.warning(f'{attr_name} found in input file but the '
                                   'datetime format is not supported and the '
                                   'attribute has therefore been ignored')
                    continue
            granule.meta[attr_name] = attr_value

    for attr_name in specs.SUPPORTED_ATTRIBUTES:
        if attr_name in granule.meta.keys():
            continue
        if hasattr(f_handler, attr_name):
            granule.meta[attr_name] = getattr(f_handler, attr_name)

    for attr_name in specs.CF_ATTRIBUTES:
        if attr_name in granule.meta.keys():
            continue
        if hasattr(f_handler, attr_name):
            granule.meta[attr_name] = getattr(f_handler, attr_name)

    for attr_name in specs.OPTIONAL_ATTRIBUTES:
        if attr_name in granule.meta.keys():
            continue
        if hasattr(f_handler, attr_name):
            granule.meta[attr_name] = getattr(f_handler, attr_name)

    for attr_name in specs.SPECIAL_ATTRIBUTES:
        if attr_name in granule.meta.keys():
            continue
        if hasattr(f_handler, attr_name):
            granule.meta[attr_name] = getattr(f_handler, attr_name)


def extract_variable_attributes(f_handler: netCDF4.Dataset,
                                var_id: str,
                                granule: Granule) -> None:
    """"""
    extracted_attrs = []
    specs = get_idf_specs(granule.idf_version)

    if var_id not in granule.vars.keys():
        granule.vars[var_id] = {'options': {}}

    if var_id not in f_handler.variables.keys():
        return

    src_var = f_handler.variables[var_id]
    for attr_name in specs.VARIABLE_MANDATORY_ATTRIBUTES:
        if attr_name in granule.vars[var_id].keys():
            continue
        if hasattr(src_var, attr_name):
            granule.vars[var_id][attr_name] = getattr(src_var, attr_name)
            extracted_attrs.append(attr_name)

    for attr_name in specs.VARIABLE_CF_ATTRIBUTES:
        if attr_name in granule.vars[var_id].keys():
            continue
        if hasattr(src_var, attr_name):
            granule.vars[var_id][attr_name] = getattr(src_var, attr_name)
            extracted_attrs.append(attr_name)

    for attr_name in specs.VARIABLE_OPTIONAL_ATTRIBUTES:
        if attr_name in granule.vars[var_id].keys():
            continue
        if hasattr(src_var, attr_name):
            granule.vars[var_id][attr_name] = getattr(src_var, attr_name)
            extracted_attrs.append(attr_name)

    # According to the NetCDF User Guide, valid_min and valid_max must be
    # expressed as packed values if there is an offset and a scale factor
    # but the IDF converter needs the unpacked values
    is_packed = (('add_offset' in extracted_attrs) and
                 ('scale_factor' in extracted_attrs))
    if is_packed and ('valid_min' in extracted_attrs):
        # Unpack valid_min
        offset = granule.vars[var_id]['add_offset']
        scale = granule.vars[var_id]['scale_factor']
        unpacked_value = offset + scale * granule.vars[var_id]['valid_min']
        granule.vars[var_id]['valid_min'] = unpacked_value
    if is_packed and ('valid_max' in extracted_attrs):
        # Unpack valid_max
        offset = granule.vars[var_id]['add_offset']
        scale = granule.vars[var_id]['scale_factor']
        unpacked_value = offset + scale * granule.vars[var_id]['valid_max']
        granule.vars[var_id]['valid_max'] = unpacked_value

    # Values extracted from the input file are unpacked, i.e. add_offset and
    # scale_factor have already been applied. Remove them from the variable
    # attributes to avoid confusion
    if 'scale_factor' in granule.vars[var_id].keys():
        del granule.vars[var_id]['scale_factor']
    if 'add_offset' in granule.vars[var_id].keys():
        del granule.vars[var_id]['add_offset']


def _extract_values(f_handler: netCDF4.Dataset,
                    var_id: str,
                    idx: IdxSlices,
                    value_placeholder: typing.Any,
                    mask_state: typing.Optional[bool]
                    ) -> typing.Tuple[numpy.typing.ArrayLike,
                                      typing.Optional[bool]]:
    """"""
    _idx = tuple(idx)
    band: numpy.typing.ArrayLike  # simply to declare type for mypy

    # When there is a placeholder value and automasking is active (default)
    # netCDF4 replaces missing/invalid values by the placeholder, but if
    # the placeholder value is NaN this behavior triggers Numpy warnings
    # Note: netCDF4 uses missing_value as placeholder if this attribute is
    # provided, otherwise it uses _FillValue as a fallback.
    if (value_placeholder is not None) and numpy.isnan(value_placeholder):
        f_handler.variables[var_id].set_auto_mask(False)
        band = f_handler.variables[var_id][_idx]
        band = numpy.ma.masked_invalid(band)
        if mask_state is None:
            mask_state = True
    else:
        band = f_handler.variables[var_id][_idx]

    return band, mask_state


def _extract_shifted_values(f_handler: netCDF4.Dataset,
                            var_id: str,
                            idx: IdxSlices,
                            value_placeholder: typing.Any,
                            mask_state: typing.Optional[bool],
                            shift: IdxShifts
                            ) -> typing.Tuple[numpy.typing.ArrayLike,
                                              typing.Optional[bool]]:
    """"""
    _idx = tuple(idx)
    band: numpy.typing.ArrayLike  # simply to declare type for mypy

    # When there is a placeholder value and automasking is active (default)
    # netCDF4 replaces missing/invalid values by the placeholder, but if
    # the placeholder value is NaN this behavior triggers Numpy warnings
    # Note: netCDF4 uses missing_value as placeholder if this attribute is
    # provided, otherwise it uses _FillValue as a fallback.
    if (value_placeholder is not None) and numpy.isnan(value_placeholder):
        f_handler.variables[var_id].set_auto_mask(False)
        band = f_handler.variables[var_id]
        band = numpy.ma.masked_invalid(band)
        if mask_state is None:
            mask_state = True
    else:
        band = f_handler.variables[var_id]

    for axis, amount in shift.items():
        band = numpy.roll(band, amount, axis=axis)

    return band[_idx], mask_state


def extract_variable_values(f_handler: netCDF4.Dataset,
                            var_id: str,
                            mask_state: typing.Optional[bool] = None,
                            idx: typing.Optional[IdxSlices] = None,
                            shifts: typing.Optional[IdxShifts] = None
                            ) -> numpy.typing.ArrayLike:
    """"""
    if idx is None:
        idx = [slice(None, None, None)]

    # Detected whether variable has a placeholder value for missing or
    # invalid data
    has_fill_value = hasattr(f_handler.variables[var_id], '_FillValue')
    has_missing_value = hasattr(f_handler.variables[var_id], 'missing_value')

    value_placeholder = None
    if has_missing_value:
        value_placeholder = f_handler.variables[var_id].missing_value
    elif has_fill_value:
        value_placeholder = f_handler.variables[var_id]._FillValue

    # Some netCDF files use a missing_value or a _FillValue that is not
    # compatible with the data type of the variable. The data producers should
    # fix their files because they are invalid, but it is unlikely so the
    # idf_converter considers the invalid value to be a NaN.
    if value_placeholder is not None:
        dtype = f_handler.variables[var_id].datatype
        if not numpy.can_cast(value_placeholder, dtype):
            logger.warning(f'The placeholder value {value_placeholder} for '
                           f'"{var_id}" does not match its data type')
            value_placeholder = float('nan')

    if mask_state is not None:
        f_handler.variables[var_id].set_auto_mask(mask_state)

    if (shifts is None) or (0 >= len(list(shifts.keys()))):
        band, mask_state = _extract_values(f_handler, var_id, idx,
                                           value_placeholder, mask_state)
    else:
        band, mask_state = _extract_shifted_values(f_handler, var_id, idx,
                                                   value_placeholder,
                                                   mask_state, shifts)
    if mask_state is not None:
        f_handler.variables[var_id].set_auto_mask(mask_state)

    return band


def find_whitespace(str_buffer: str) -> int:
    """"""
    return next((i for i, s in enumerate(str_buffer) if s.isspace()), -1)


def rfind_whitespace(str_buffer: str) -> int:
    """"""
    max_index = len(str_buffer) - 1
    reversed_buffer = reversed(str_buffer)
    return next((max_index - i for i, s in enumerate(reversed_buffer)
                 if s.isspace()),
                -1)


def get_next_pair(str_buffer: str, original: str, kv_separator: str,
                  offset: int) -> typing.Tuple[typing.Optional[str],
                                               typing.Optional[str],
                                               int]:
    """"""
    str_len = len(str_buffer)
    if 0 >= str_len:
        return (None, None, offset)

    i_equal = str_buffer.find(kv_separator, offset)

    # Find key
    tmp_buffer = str_buffer[0:i_equal].rstrip()
    i_key = 1 + rfind_whitespace(tmp_buffer)
    key = original[i_key:i_equal].strip()

    # Find value
    i_value_start = str_len - len(str_buffer[(1 + i_equal):].lstrip())
    first_char = str_buffer[i_value_start]
    if first_char in ('"', "'"):
        i_value_stop = str_buffer.find(first_char, 1 + i_value_start)
        if 0 > i_value_stop:
            i_value_stop = str_len
        value = original[i_value_start:i_value_stop]
        i_value_stop = min(1 + i_value_stop, str_len)
        value = value[1:]  # ending quote is already gone but starting remains
    else:
        tmp_buffer = str_buffer[i_value_start:]
        i_next_equal = str_buffer.find(kv_separator, i_value_start)
        if 0 > i_next_equal:
            i_value_stop = str_len
        else:
            tmp_buffer = str_buffer[0:i_next_equal].rstrip()
            i_value_stop = rfind_whitespace(tmp_buffer)
        value = original[i_value_start:i_value_stop].strip()
    new_offset = i_value_stop
    return (key, value, new_offset)


def parse_opt(text: str, pair_separator: str,
              kv_separator: str) -> typing.Iterator[typing.Tuple[str, str]]:
    """"""
    # Remove spaces on both ends of the string
    stripped_text = text.strip()

    if ' ' != pair_separator:
        stripped_text = stripped_text.replace(pair_separator, ' ')

    offset = 0
    str_len = len(stripped_text)
    while offset < str_len - 1:
        key, value, offset = get_next_pair(stripped_text, text,
                                           kv_separator, offset)
        if (key is not None) and (value is not None):
            yield (key, value)


def apply_global_overrides(input_opts: InputOptions, granule: Granule) -> None:
    """
    Global overrides are provided as a comma-separated list of key:value.
    No space is allowed around the separating comma.
    No trailing comma.
    Values cannot contain an equal sign.
    """
    specs = get_idf_specs(granule.idf_version)
    attrs_str = input_opts.get('global_overrides', None)
    if attrs_str is None:
        return
    attrs = parse_opt(attrs_str, ',', ':')
    for _attr_name, _attr_value in attrs:
        attr_name = _attr_name.strip()
        attr_value = _attr_value.strip()
        is_time_coverage_attr = (attr_name in ('time_coverage_start',
                                               'time_coverage_end'))
        if is_time_coverage_attr and isinstance(attr_value, str):
            _parse_datetime = idf_converter.lib.time.parse_datetime
            time_coverage_fmt = input_opts.get('time_coverage_format', None)
            try:
                dt_value = _parse_datetime(attr_value, time_coverage_fmt)
            except idf_converter.lib.time.InvalidDatetimeFormat:
                logger.warning(f'{attr_name} found in input file but the '
                               'datetime format is not supported and the '
                               'attribute has therefore been ignored')
                raise InvalidTimeCoverageOverride(attr_name, attr_value)
            granule.meta[attr_name] = dt_value
        elif attr_name in specs.NUMERICAL_ATTRIBUTES:
            granule.meta[attr_name] = float(attr_value)
        else:
            granule.meta[attr_name] = attr_value


def apply_var_overrides(input_opts: InputOptions, granule: Granule) -> None:
    """"""
    specs = get_idf_specs(granule.idf_version)

    for override_key in input_opts.keys():
        if not override_key.startswith('override('):
            continue

        var_id = override_key.strip()[9:-1]
        attrs_str = input_opts[override_key]
        attrs = parse_opt(attrs_str, ',', ':')
        for _attr_name, _attr_value in attrs:
            attr_name = _attr_name.strip()
            attr_value = _attr_value.strip()
            if var_id not in granule.vars.keys():
                granule.vars[var_id] = {'options': {}}

            if attr_name in specs.VARIABLE_NUMERICAL_ATTRIBUTES:
                auto_attr = attr_name in ('valid_min', 'valid_max')
                if (auto_attr is True) and ('auto' == attr_value):
                    granule.vars[var_id][attr_name] = attr_value
                else:
                    granule.vars[var_id][attr_name] = float(attr_value)
            else:
                granule.vars[var_id][attr_name] = attr_value


def build_flag_mask(var_id: str,
                    band: numpy.typing.NDArray,
                    flag_band: numpy.typing.NDArray,
                    granule: Granule,
                    ) -> numpy.typing.NDArray:

    """"""
    flag_var_id = granule.vars[var_id].pop('flag_variable', None)
    flag_min_value = granule.vars[var_id].pop('flag_min', None)
    flag_max_value = granule.vars[var_id].pop('flag_max', None)

    has_flag_var = (flag_var_id is not None)
    has_flag_criteria = ((flag_min_value is not None) or
                         (flag_max_value is not None))
    if (has_flag_var and has_flag_criteria) is False:
        band_shape = numpy.shape(band)
        default_mask: numpy.typing.NDArray
        default_mask = numpy.ma.make_mask_none(band_shape)
        return default_mask

    _qual: numpy.typing.NDArray
    _qual = numpy.ma.masked_array(flag_band)

    # _mask = True when the data should be considered invalid, i.e. when:

    # - the flag variable is masked (i.e. no information on data quality)
    _mask: numpy.typing.NDArray = numpy.ma.getmaskarray(_qual)

    # - the value of the flag variable is strictly below the lower theshold
    if flag_min_value is not None:
        _mask = (_mask | (_qual < int(flag_min_value)))

    # - the value of the flag variable is strictly above the upper threshold
    if flag_max_value is not None:
        _mask = (_mask | (_qual > int(flag_max_value)))

    return _mask


def add_virtual_variables(output_opts: OutputOptions,
                          transforms: TransformsList
                          ) -> None:
    """"""
    virtual_var_ids = []
    for key in output_opts.keys():
        if key.startswith('add_variables('):
            var_ids_str = key[14:-1]
            var_ids = [_.strip() for _ in var_ids_str.split(',')
                       if 0 < len(_.strip())]
            var_cfg = output_opts[key]
            _transform_attrs = idf_converter.lib.parse_opt(var_cfg, ',', ':')
            transform_attrs: typing.Dict[str, typing.Any] = {}
            for name, value in _transform_attrs:
                if ';' in value:
                    transform_attrs[name] = [_.strip()
                                             for _ in value.split(';')
                                             if 0 < len(_.strip())]
                else:
                    try:
                        transform_attrs[name] = float(value.strip())
                    except ValueError:
                        _value = value.strip()
                        if _value.lower() in ('yes', 'true'):
                            transform_attrs[name] = True
                        elif _value.lower() in ('no', 'false'):
                            transform_attrs[name] = False
                        else:
                            transform_attrs[name] = _value

            if 'using' not in transform_attrs.keys():
                raise MissingVirtualVariableTransformName(var_ids_str)
            transform_name = transform_attrs.pop('using')
            transforms.append((transform_name, transform_attrs))
            virtual_var_ids.extend(var_ids)

    exported_ids = output_opts.get('__export', [])
    exported_ids.extend(virtual_var_ids)

    # Make sure there are no duplicates
    exported_ids = list(set(exported_ids))

    output_opts['__export'] = exported_ids


def remove_variables(output_opts: OutputOptions,
                     transforms: TransformsList
                     ) -> None:
    """"""
    if 'remove_variables' in output_opts.keys():
        var_ids = [_.strip()
                   for _ in output_opts['remove_variables'].split(',')]
        if 0 < len(var_ids):
            transforms.append(('remove_vars', {'targets': var_ids}))


def _safe_mod_angle(num: numpy.typing.NDArray,
                    denom: float,
                    decimals: int
                    ) -> typing.Tuple[numpy.typing.NDArray, bool]:
    """"""
    # The difference between angles (or longitudes) values read from the input
    # file might be very small values: having such values might cause underflow
    # errors when calling the numpy implementation of modulo.
    # As a workaround, since we know that angles/longitudes are not meant to
    # reach very high values we can multiply both operands of the modulo
    # function by a fixed factor > 1 to avoid the underflows and then divide
    # the result by the same factor to get the actual result.
    # The uflow_fix variable will play the role of the fixed factor in this
    # method.

    values: numpy.typing.NDArray
    values_truncated_to_0 = False
    try:
        values = numpy.mod(num, denom)
    except FloatingPointError:
        uflow_fix = 10 ** decimals

        _rounded_num = numpy.round(num, decimals=decimals)
        _scaled_num = uflow_fix * _rounded_num
        _scaled_denom = uflow_fix * denom

        mask = (numpy.abs(_scaled_num) < 1.0)  # i.e. |angle| < 10^-decimals
        if mask.any():
            _scaled_num[numpy.where(mask)] = 0.0
            values_truncated_to_0 = True

        _values = numpy.mod(_scaled_num,
                            _scaled_denom,
                            where=numpy.isfinite(_scaled_num))

        # Make sure that dividing by uflow_fix will not trigger an underflow
        eps = numpy.finfo(num.dtype).eps
        underflow_mask = (numpy.abs(_values) < uflow_fix * eps)
        if underflow_mask.any():
            _values[numpy.where(underflow_mask)] = 0.0
            values_truncated_to_0 = True

        values = _values / uflow_fix
    return values, values_truncated_to_0


def mod360(num: numpy.typing.NDArray,
           decimals: int
           ) -> typing.Tuple[numpy.typing.NDArray, bool]:
    """"""
    return _safe_mod_angle(num, 360.0, decimals)


def mod2pi(num: numpy.typing.NDArray,
           decimals: int
           ) -> typing.Tuple[numpy.typing.NDArray, bool]:
    """"""
    return _safe_mod_angle(num, 2 * numpy.pi, decimals)
