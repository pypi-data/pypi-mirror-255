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

"""This module provides methods to serialize Granules objects into IDF files.
"""

import os
import typing
import logging
import netCDF4
import idf_converter.lib
import idf_converter.lib.downscale
from idf_converter.lib.types import InputOptions, OutputOptions, Granule

logger = logging.getLogger(__name__)


class NCCreateDimError(Exception):
    """Error raised when the netCDF4 module failed to create a dimension on
    the IDF output file."""

    def __init__(self, dim_name: str, dim_size: int) -> None:
        msg = (f'Error while creating netCDF dimension with name={dim_name} '
               f'and size={dim_size}')
        super(NCCreateDimError, self).__init__(msg)


def help() -> typing.Tuple[str, str]:
    """"""
    inp = ('',)
    out = ('    downscale\tRequest production of IDF files at degraded'
           ' resolutions in addition to the full resolution file. Valid'
           ' values are "true", "yes", "1" (defaults to "no"). Please note'
           ' that downscaling is not supported for time-dependent granules.',)
    return ('\n'.join(inp), '\n'.join(out))


def close_and_remove(idf_file: netCDF4.Dataset) -> None:
    """Close and delete an IDF file after an error.

    Parameters
    ----------
    idf_file: netCDF4.Dataset
        NetCDF4 handle for the IDF file to close and delete.
    """
    filepath = idf_file.filepath()
    idf_file.close()
    os.remove(filepath)


def as_idf(original_input_opts: InputOptions,
           original_output_opts: OutputOptions,
           original_granule: Granule) -> None:
    """Create IDF file from granule information.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format
    granule: idf_converter.lib.Granule
        Object representing the granule data and metadata
    """

    fmt = idf_converter.lib.get_idf_formatter(original_granule.idf_version)

    prepared = fmt.preformat(original_input_opts, original_output_opts,
                             original_granule)

    for input_opts, output_opts, granule in prepared:
        # Create dataset
        output_dir, idf_fname = fmt.get_idf_path(input_opts, output_opts,
                                                 granule)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, idf_fname)
        idf_file = netCDF4.Dataset(output_path, mode='w', format='NETCDF4',
                                   clobber=True)

        # IDF-specific formatting
        formatted = fmt.granule2idf(input_opts, output_opts, granule, idf_file)
        processed_dims, processed_vars, processed_attrs = formatted

        dimensions = granule.dims
        attributes = granule.meta
        variables = granule.vars

        # Add other dimensions
        for dim_name, dim_size in dimensions.items():
            if dim_name in processed_dims:
                continue

            try:
                idf_file.createDimension(dim_name, dim_size)
            except Exception:  # TODO: use more specific exception catching
                close_and_remove(idf_file)
                raise NCCreateDimError(dim_name, dim_size)

            processed_dims.append(dim_name)

        # Add other attributes
        for attrname, attrval in attributes.items():
            if attrname in processed_attrs:
                continue
            setattr(idf_file, attrname, attrval)

        idf_file.sync()

        # Variables
        specs = idf_converter.lib.get_idf_specs(granule.idf_version)
        for var_id in variables.keys():
            if var_id in processed_vars:
                continue
            tmp_res = fmt.write_variable(var_id, granule, idf_file, specs)
            _var, processed_var_attrs = tmp_res
            for var_attr in granule.vars[var_id].keys():
                if var_attr not in processed_var_attrs:
                    logger.warning(f'{var_attr} not processed for {var_id}')
            idf_file.sync()

        logger.debug('Downscaling...')
        _downscale = output_opts.get('downscale', 'no')
        downscale = _downscale.lower() in ('true', 'yes', '1')
        if downscale:
            idf_converter.lib.downscale.downscale(output_path)

        idf_file.close()
