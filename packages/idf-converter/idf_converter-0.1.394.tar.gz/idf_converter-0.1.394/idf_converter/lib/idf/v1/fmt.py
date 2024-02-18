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

"""This module provides methods to format granules according to version 1.x of
the IDF format."""

import os
import numpy
import typing
import logging
import netCDF4
import datetime
import idf_converter
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ProcessedLists
from idf_converter.lib.types import Granule, FormatterResult, TransformsList
try:
    import importlib.metadata
    idf_converter_version = importlib.metadata.version('idf_converter')
except ImportError:
    import pkg_resources
    _idf_converter_pkg = pkg_resources.get_distribution('idf_converter')
    idf_converter_version = _idf_converter_pkg.version

logger = logging.getLogger(__name__)
Granule2IDFResult = typing.Optional[ProcessedLists]
WriteVariableResult = typing.Tuple[netCDF4.Variable, typing.List[str]]


class MissingInputPath(ValueError):
    """Error raised if the "path" key is missing from the input options."""
    pass


class MissingOutputPath(ValueError):
    """Error raised if the "path" key is missing from the output options."""
    pass


class MissingCollection(ValueError):
    """Error raised if the "collection" key is missing from the output
    options."""
    pass


class MissingExportList(ValueError):
    """Error raised if the "__export" key is either missing or associated with
    an empty list in the output options."""
    pass


class DataModelNotSupported(ValueError):
    """Error raised when the granule to convert has a data model which is not
    supported by this version of IDF.

    Parameters
    ----------
    data_model: str
        Data model associated with the granule to convert and which is not
        supported by this version of the IDF format
    """
    def __init__(self, data_model: str) -> None:
        """"""
        self.data_model = data_model
        super(DataModelNotSupported, self).__init__()


def help() -> typing.Tuple[str, str]:
    """"""
    inp = ('',)  # "path" is required but will also be claimed by readers
    out = ('    path\tPath of the directory where the IDF files will be saved',
           '    collection\tName of the collection that will own the IDF files'
           ' produced by the converter',
           )
    return ('\n'.join(inp), '\n'.join(out))


def apply_data_storage_policy(input_opts: InputOptions,
                              output_opts: OutputOptions,
                              granule: Granule,
                              transforms: TransformsList
                              ) -> None:
    """"""
    def _lazy_eval_ubyte_export(output_opts: OutputOptions,
                                granule: Granule
                                ) -> typing.Iterator[str]:
        output_var_ids = output_opts.get('__export', None)
        if (output_var_ids is None) or (0 >= len(output_var_ids)):
            raise MissingExportList()

        _float_variables = output_opts.get('use_float32_values', '')
        float_variables = [_.strip() for _ in _float_variables.split(',')
                           if 0 < len(_.strip())]
        var_names = {_: granule.vars[_]['name'] for _ in output_var_ids}
        for var_id in output_var_ids:
            if var_names[var_id] not in float_variables:
                yield var_id

    def _lazy_eval_float_export(output_opts: OutputOptions,
                                granule: Granule
                                ) -> typing.Iterator[str]:
        output_var_ids = output_opts.get('__export', None)
        if (output_var_ids is None) or (0 >= len(output_var_ids)):
            raise MissingExportList()

        _float_variables = output_opts.get('use_float32_values', '')
        float_variables = [_.strip() for _ in _float_variables.split(',')
                           if 0 < len(_.strip())]
        var_names = {_: granule.vars[_]['name'] for _ in output_var_ids}
        for var_id in output_var_ids:
            if var_names[var_id] in float_variables:
                yield var_id

    # PACKING AS UBYTES
    # It automatically sets NaN and masked values to fill value (255)
    transforms.append(('store_as_ubytes',
                       {'targets': _lazy_eval_ubyte_export(output_opts,
                                                           granule)}))

    # STORING AS FLOAT32
    transforms.append(('store_as_float32',
                       {'targets': _lazy_eval_float_export(output_opts,
                                                           granule)}))


def preformat(input_opts: InputOptions,
              output_opts: OutputOptions,
              granule: Granule) -> typing.Iterator[FormatterResult]:
    """"""
    data_model_mod = get_data_model(granule.data_model)
    subgranules = data_model_mod.preformat(input_opts, output_opts, granule)
    for subgranule in subgranules:
        original_id = subgranule[2].meta['idf_granule_id']
        granule_id_prefix = output_opts.get('id_prefix', '')
        if 'INPUT_FILENAME' == granule_id_prefix:
            input_filename = os.path.basename(input_opts['path'])
            granule_id_prefix, _ = os.path.splitext(input_filename)
            if granule_id_prefix.endswith('_') is False:
                granule_id_prefix = f'{granule_id_prefix}_'
        granule_id_suffix = output_opts.get('id_suffix', '')
        if 'INPUT_FILENAME' == granule_id_suffix:
            input_filename = os.path.basename(input_opts['path'])
            granule_id_suffix, _ = os.path.splitext(input_filename)
            if granule_id_suffix.startswith('_') is False:
                granule_id_suffix = f'_{granule_id_prefix}'
        new_id = f'{granule_id_prefix}{original_id}{granule_id_suffix}'
        subgranule[2].meta['idf_granule_id'] = new_id
        yield subgranule


def get_idf_path(input_opts: InputOptions,
                 output_opts: OutputOptions,
                 granule: Granule) -> typing.Tuple[str, str]:
    """Build the path of the granule directory and the name of the IDF file
    from the input and ouput options.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.types.Granule
        Object representing the granule data and metadata

    Returns
    -------
    tuple
        A tuple containing two elements:

        - the path of the granule directory
        - the name of the IDF file
    """
    output_dir = output_opts.get('path', None)
    if output_dir is None:
        raise MissingOutputPath()

    collection = output_opts.get('collection', None)
    if collection is None:
        raise MissingCollection()

    collection_dir = os.path.join(output_dir, collection)

    input_path = input_opts.get('path', None)
    if input_path is None:
        raise MissingInputPath()

    granule_name = granule.meta['idf_granule_id']
    granule_dir = os.path.join(collection_dir, granule_name)
    idf_name = f'{granule_name}_idf_00.nc'
    return (granule_dir, idf_name)


def _to_numerical(str_value: str) -> float:
    """"""
    try:
        result = float(str_value)
    except ValueError:
        try:
            result = float(''.join([c for c in str_value
                                    if c.isdigit() or '.' == c]))
        except ValueError:
            result = float('nan')
    return result


def _to_spec_time_format(time_obj: typing.Any, specs: typing.Any) -> str:
    """"""
    _time_obj = time_obj
    if not isinstance(_time_obj, datetime.datetime):
        # ctime objects use time.strftime which does not support the %f format
        # for microseconds, so convert to regular datetime object
        _time_obj = time_obj._to_real_datetime()
    result = str(_time_obj.strftime(specs.TIMEFMT))
    return result


def write_variable(var_id: str,
                   granule: Granule,
                   idf_file: netCDF4.Dataset,
                   specs: typing.Any) -> WriteVariableResult:
    """"""
    var_dict = granule.vars[var_id]

    logger.debug(f'write variable {var_id}')

    # Options
    zlib = var_dict['options'].get('zlib', True)
    complevel = var_dict['options'].get('complevel', 4)
    shuffle = var_dict['options'].get('shuffle', True)
    fletcher32 = var_dict['options'].get('fletcher32', False)
    contiguous = var_dict['options'].get('contiguous', False)
    chunksizes = var_dict['options'].get('chunksizes', None)
    endian = var_dict['options'].get('endian', 'native')
    ls_digit = var_dict['options'].get('least_significant_digit', None)

    # Create variable
    dims = var_dict['options'].get('dimensions', None)
    if dims is None:
        dims = granule.get_data_model_dimensions()
        extra_dims = var_dict['options'].get('extra_dimensions', None)
        if extra_dims is not None:
            dims = dims + list(extra_dims)
    var_name = var_dict['name']
    dtype = var_dict['array'].dtype
    fill_value = dtype.type(var_dict['_FillValue'])
    _value = idf_file.createVariable(var_name, dtype, dims,
                                     zlib=zlib, complevel=complevel,
                                     shuffle=shuffle, fletcher32=fletcher32,
                                     contiguous=contiguous,
                                     chunksizes=chunksizes, endian=endian,
                                     least_significant_digit=ls_digit,
                                     fill_value=fill_value)

    # Assign data
    value = var_dict['array']
    if len(dims) == (1 + len(value.shape)):
        _value[:] = value[numpy.newaxis, :]
    else:
        _value[:] = value[:]

    if 'add_offset' in var_dict.keys():
        _value.add_offset = numpy.float32(var_dict['add_offset'])
    if 'scale_factor' in var_dict.keys():
        _value.scale_factor = numpy.float32(var_dict['scale_factor'])

    processed_var_attrs = ['name', 'add_offset', 'scale_factor', '_FillValue',
                           'options', 'dimensions', 'array', 'datatype']

    for attr in specs.VARIABLE_MANDATORY_ATTRIBUTES:
        if attr in var_dict.keys() and not hasattr(_value, attr):
            value = var_dict[attr]
            if attr in specs.VARIABLE_TEXT_ATTRIBUTES:
                setattr(_value, attr, str(value).encode('utf-8'))
            else:
                setattr(_value, attr, value)
            processed_var_attrs.append(attr)

    # CF attributes
    for attr in specs.VARIABLE_CF_ATTRIBUTES:
        if attr in var_dict.keys():
            value = var_dict[attr]

            # Make sure valid_min and valid_max use the right type
            if attr in ('valid_min', 'valid_max'):
                value = dtype.type(value)
                setattr(_value, attr, value)
            elif attr in specs.VARIABLE_TEXT_ATTRIBUTES:
                setattr(_value, attr, str(value).encode('utf-8'))
            else:
                setattr(_value, attr, value)
            processed_var_attrs.append(attr)

    # Optional attributes
    for attr in specs.VARIABLE_OPTIONAL_ATTRIBUTES:
        if attr in var_dict:
            value = var_dict[attr]
            if attr in specs.VARIABLE_TEXT_ATTRIBUTES:
                setattr(_value, attr, str(value).encode('utf-8'))
            else:
                setattr(_value, attr, value)
            processed_var_attrs.append(attr)

    return (_value, processed_var_attrs)


def write_global_attributes(input_opts: InputOptions,
                            output_opts: OutputOptions,
                            granule: Granule,
                            idf_file: netCDF4.Dataset,
                            specs: typing.Any) -> typing.List[str]:
    """Write global attributes to an IDF file. Attributes not defined in the
    IDF format specifications will be ignored.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.types.Granule
        Object representing the granule data and metadata
    idf_file: netCDF4.Dataset
        Handle of the IDF file to edit
    specs: module
        Module which contains the specifications for the IDF format

    Returns
    -------
    list
        The list of attributes that the method has included in the IDF file
    """
    # Mandatory attributes
    start_dt = _to_spec_time_format(granule.meta['time_coverage_start'], specs)
    stop_dt = _to_spec_time_format(granule.meta['time_coverage_end'], specs)

    spatial_resolution = numpy.float32(granule.meta['idf_spatial_resolution'])
    subsampling_factor = numpy.int32(0)  # Hardcoded
    spatial_resolution_units = b'm'  # Hardcoded

    logger.warning('idf_subsampling_factor value is hardcoded to "0"')
    logger.warning('idf_spatial_resolution_units value is hardcoded to "m"')

    idf_file.idf_version = granule.idf_version.encode('utf-8')
    idf_file.idf_granule_id = granule.meta['idf_granule_id'].encode('utf-8')
    idf_file.time_coverage_start = start_dt.encode('utf-8')
    idf_file.time_coverage_end = stop_dt.encode('utf-8')
    idf_file.idf_subsampling_factor = subsampling_factor
    idf_file.idf_spatial_resolution = spatial_resolution
    idf_file.idf_spatial_resolution_units = spatial_resolution_units

    processed_attrs = ['idf_version', 'idf_granule_id', 'time_coverage_start',
                       'time_coverage_end', 'idf_subsampling_factor',
                       'idf_spatial_resolution',
                       'idf_spatial_resolution_units']

    for attr in specs.MANDATORY_ATTRIBUTES:
        if attr in granule.meta and attr not in processed_attrs:
            if attr in specs.NUMERICAL_ATTRIBUTES:
                setattr(idf_file, attr, _to_numerical(granule.meta[attr]))
            elif attr in specs.TEXT_ATTRIBUTES:
                setattr(idf_file, attr,
                        str(granule.meta[attr]).encode('utf-8'))
            else:
                setattr(idf_file, attr, granule.meta[attr])
            processed_attrs.append(attr)

    # Supported attributes
    for attr in specs.SUPPORTED_ATTRIBUTES:
        if attr in granule.meta:
            if attr in specs.NUMERICAL_ATTRIBUTES:
                setattr(idf_file, attr, _to_numerical(granule.meta[attr]))
            elif attr in specs.TEXT_ATTRIBUTES:
                setattr(idf_file, attr,
                        str(granule.meta[attr]).encode('utf-8'))
            else:
                setattr(idf_file, attr, granule.meta[attr])
            processed_attrs.append(attr)

    # CF attributes
    idf_software = f'{idf_converter.__package__} {idf_converter_version}'
    _processing_software = granule.meta.get('processing_software', None)
    if _processing_software is None or 0 <= len(_processing_software):
        processing_software = idf_software
    else:
        processing_software = f'{_processing_software}\n{idf_software}'
    idf_file.processing_software = processing_software.encode('utf-8')
    processed_attrs.append('processing_software')

    now = datetime.datetime.utcnow()
    idf_history = f'{now:%Y-%m-%dT%H:%M:%SZ} Conversion to IDF'
    _history = granule.meta.get('history', None)
    if _history is None or 0 <= len(_history):
        history = idf_history
    else:
        history = f'{_history}\n{idf_history}'
    idf_file.history = history.encode('utf-8')
    processed_attrs.append('history')

    for attr in specs.CF_ATTRIBUTES:
        if attr in granule.meta and attr not in processed_attrs:
            if attr in specs.NUMERICAL_ATTRIBUTES:
                setattr(idf_file, attr, _to_numerical(granule.meta[attr]))
            elif attr in specs.TEXT_ATTRIBUTES:
                setattr(idf_file, attr,
                        str(granule.meta[attr]).encode('utf-8'))
            else:
                setattr(idf_file, attr, granule.meta[attr])
            processed_attrs.append(attr)

    # Optional attributes
    idf_file.netcdf_version_id = netCDF4.getlibversion().encode('utf-8')
    processed_attrs.append('netcdf_version_id')

    for attr in specs.OPTIONAL_ATTRIBUTES:
        if attr in granule.meta and attr not in processed_attrs:
            if attr in specs.NUMERICAL_ATTRIBUTES:
                setattr(idf_file, attr, _to_numerical(granule.meta[attr]))
            elif attr in specs.TEXT_ATTRIBUTES:
                setattr(idf_file, attr,
                        str(granule.meta[attr]).encode('utf-8'))
            else:
                setattr(idf_file, attr, granule.meta[attr])
            processed_attrs.append(attr)

    if not hasattr(idf_file, 'license'):
        _license = b'IDF protocol describes data use as free and open'
        idf_file.license = _license
        processed_attrs.append('license')

    if not hasattr(idf_file, 'standard_name_vocabulary'):
        _std_voc = b'NetCDF Climate and Forecast (CF) Metadata Convention'
        idf_file.standard_name_vocabulary = _std_voc
        processed_attrs.append('standard_name_vocabulary')

    # Special attributes
    for attr in specs.SPECIAL_ATTRIBUTES:
        if attr in granule.meta and attr not in processed_attrs:
            if attr in specs.NUMERICAL_ATTRIBUTES:
                setattr(idf_file, attr, _to_numerical(granule.meta[attr]))
            elif attr in specs.TEXT_ATTRIBUTES:
                setattr(idf_file, attr,
                        str(granule.meta[attr]).encode('utf-8'))
            else:
                setattr(idf_file, attr, granule.meta[attr])
            processed_attrs.append(attr)

    return processed_attrs


def get_data_model(data_model: str) -> typing.Any:
    """"""
    mod = None
    _data_model = data_model.lower()
    if 'time_dependent' == _data_model:
        import idf_converter.lib.idf.v1.time_dependent
        mod = idf_converter.lib.idf.v1.time_dependent
    elif 'swath' == _data_model:
        import idf_converter.lib.idf.v1.swath
        mod = idf_converter.lib.idf.v1.swath
    elif 'grid_yx' == _data_model:
        import idf_converter.lib.idf.v1.grid_yx
        mod = idf_converter.lib.idf.v1.grid_yx
    elif 'grid_latlon' == _data_model:
        import idf_converter.lib.idf.v1.grid_latlon
        mod = idf_converter.lib.idf.v1.grid_latlon
    else:
        raise DataModelNotSupported(data_model)

    return mod


def granule2idf(input_opts: InputOptions,
                output_opts: OutputOptions,
                granule: Granule,
                idf_file: netCDF4.Dataset) -> Granule2IDFResult:
    """
    Create dimensions, variables and attributes required by the IDF format
    based on granule information.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.types.Granule
        Object representing the granule data and metadata
    idf_file: netCDF4.Dataset
        Handle of the IDF file to edit

    Returns
    -------
    tuple
        Information about granule information that the method has processed.
        The tuple contains three lists::
        - a list of names for the dimensions created by the method
        - a list of identifiers for the variables created by the method
        - a list of names for the attributes created by the method
    """
    data_model_mod = get_data_model(granule.data_model)
    format_granule = data_model_mod.format_granule

    dims_done, vars_done, attrs_done = format_granule(input_opts, output_opts,
                                                      granule, idf_file)

    specs = idf_converter.lib.get_idf_specs(granule.idf_version)
    processed_attrs = write_global_attributes(input_opts, output_opts, granule,
                                              idf_file, specs)
    attrs_done.extend(processed_attrs)

    return (dims_done, vars_done, attrs_done)
