# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-27
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

import os
import numpy
import typing
import netCDF4
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'


class InputPathMissing(IOError):
    """"""
    pass


class MissingVariablesList(Exception):
    """Error raised when the "variables" input option has not been specified
    by the user."""
    pass


class MaskedCoordinatesError(Exception):
    """Error raised when masked values are found in longitudes or latitudes
    even after removing the leading and trailing rows where coordinates are
    completely masked."""
    pass


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def read_data(input_opts: InputOptions,
              output_opts: OutputOptions
              ) -> typing.Iterator[ReaderResult]:
    """Read input file, extract data and metadata, store them in a Granule
    object then prepare formatting instructions to finalize the conversion to
    IDF format.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule, list)
        A tuple which contains four elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the extracted information
          has been stored

        - a :obj:list of :obj:dict describing the formatting operations that
          the converter must perform before serializing the result in IDF
          format
    """

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    idf_converter.lib.apply_global_overrides(input_opts, granule)
    idf_converter.lib.apply_var_overrides(input_opts, granule)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        raise MissingVariablesList()
    var_ids = [x.strip() for x in _var_ids.split(',')]

    extract_variable_values = idf_converter.lib.extract_variable_values
    input_path = os.path.normpath(_input_path)
    f_handler = netCDF4.Dataset(input_path, 'r')
    lon = extract_variable_values(f_handler, 'lon')
    lat = extract_variable_values(f_handler, 'lat')
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)

    final_shape = numpy.shape(lon)
    track_slice = slice(None, None, None)
    scan_slice = slice(None, None, None)
    time_slice = slice(0, 1, None)

    lon_mask = numpy.ma.getmaskarray(lon)
    lat_mask = numpy.ma.getmaskarray(lat)
    coords_masked = (lon_mask | lat_mask)
    if coords_masked.all():
        logger.warning('All coordinates are masked. Skipping this file.')
        raise idf_converter.lib.EarlyExit()

    # Compute alongtrack slice after removing leading and trailing rows that
    # contain only masked coordinates
    rows_mask = numpy.logical_and.reduce(coords_masked, axis=1)
    valid_rows_ind = numpy.where(~rows_mask)
    track_slice = slice(valid_rows_ind[0][0], 1 + valid_rows_ind[0][-1])
    data_slices = [time_slice, track_slice, scan_slice]
    if 0 < track_slice.start:
        msg = 'Coordinates were masked in the {} first rows'
        logger.info(msg.format(track_slice.start))
    if track_slice.stop < final_shape[0]:
        msg = 'Coordinates were masked in the {} last rows'
        logger.info(msg.format(final_shape[0] - track_slice.stop))

    # Remove rows without coordinates from lon, lat and quality mask
    lon = lon[track_slice, :]
    lat = lat[track_slice, :]
    final_shape = numpy.shape(lon)

    # Check that there are no masked coordinates anymore
    lon_mask = numpy.ma.getmaskarray(lon)
    lat_mask = numpy.ma.getmaskarray(lat)
    coords_masked = (lon_mask | lat_mask)
    if coords_masked.any():
        raise MaskedCoordinatesError()

    masked_var_count = 0
    for var_id in var_ids:
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        if var_id in f_handler.variables.keys():
            band = extract_variable_values(f_handler, var_id, idx=data_slices)
        else:
            # MODIS A files are not homogenous: some files contain
            # chlorophyll_a and K_490 whereas other files don't. IDF granule
            # *must* be homogenous so we create these variables and assign
            # them a fully masked array.
            msg = 'Variable {} is missing, a placeholder is used instead'
            logger.warning(msg.format(var_id))
            band = numpy.ma.masked_all(final_shape, float)

        # Apply flag mask
        flag_var_id = granule.vars[var_id].get('flag_variable', None)
        if flag_var_id is not None:
            flag_band = f_handler.variables[flag_var_id][data_slices]
            mask = idf_converter.lib.build_flag_mask(var_id, band, flag_band,
                                                     granule)
            # Transform mask so that it has the same number of dimensions as
            # the data band, assuming data band dimensions come last in the
            # dimensions list of the mask
            while len(mask.shape) > len(band.shape):
                mask = mask[0]
            band = numpy.ma.masked_where(mask, band)

        band_masked = False
        if numpy.ma.getmaskarray(band).all():
            band_masked = True
            masked_var_count = masked_var_count + 1

        granule.vars[var_id]['array'] = band
        granule.vars[var_id]['datatype'] = band.dtype
        if 'name' not in granule.vars[var_id].keys():
            granule.vars[var_id]['name'] = var_id

        finite_ind = numpy.where(numpy.isfinite(band))
        if granule.vars[var_id].get('valid_min', None) in (None, 'auto'):
            vmin = 0.0
            if band_masked:
                logger.warning('Impossible to compute a valid_min '
                               f'automatically for {var_id} because all the '
                               f'values are masked. Using {vmin} by default.')
            else:
                vmin = numpy.nanmin(band[finite_ind])
            granule.vars[var_id]['valid_min'] = vmin

        if granule.vars[var_id].get('valid_max', None) in (None, 'auto'):
            vmax = 1.0
            if band_masked:
                logger.warning('Impossible to compute a valid_max '
                               f'automatically for {var_id} because all the '
                               f'values are masked. Using {vmax} by default.')
            else:
                vmax = numpy.nanmax(band[finite_ind])
            granule.vars[var_id]['valid_max'] = vmax

    if masked_var_count >= len(var_ids):
        # All variables are fully masked, exit early to avoid the creation of
        # a useless IDF file
        raise idf_converter.lib.EarlyExit()

    nrow, ncell = numpy.shape(lon)
    start_dt = datetime.datetime.strptime(f_handler.start_time,
                                          '%Y%m%dT%H%M%SZ')
    stop_dt = datetime.datetime.strptime(f_handler.stop_time, '%Y%m%dT%H%M%SZ')
    f_handler.close()

    granule_file = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_file)

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 1000
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['idf_granule_id'] = f'{granule_name}'
    granule.dims['row'] = int(nrow)
    granule.dims['cell'] = int(ncell)

    # Format spatial information
    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    # Add transforms
    transforms: TransformsList = []

    output_opts['__export'] = var_ids

    yield (input_opts, output_opts, granule, transforms)
