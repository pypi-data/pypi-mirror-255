# vim: ts=4:sts=4:sw=4
#
# @date 2019-10-01
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
import numpy.typing
import typing
import netCDF4
import logging
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import Granule

logger = logging.getLogger(__name__)

MasksDict = typing.Dict[str, numpy.typing.NDArray]
DATA_MODEL = 'SWATH'

# S-2 : 665, 560, 490
# red : 650 nm
# green : 510 nm
# blue : 475 nm
# https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-olci/overview/heritage  # noqa
# https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-olci/level-1/fr-or-rr-toa-radiances  # noqa
# Oa1   400 	15
# Oa2 	412.5 	10
# Oa3 	442.5 	10
# Oa4 	490 	10   BLUE
# Oa5 	510 	10
# Oa6 	560 	10   GREEN
# Oa7 	620 	10
# Oa8 	665 	10   RED
# Oa9 	673.75 	7.5
# Oa10 	681.25 	7.5
# Oa11 	708.75 	10
# Oa12 	753.75 	7.5
# Oa13 	761.25 	2.5
# Oa14 	764.375 3.75
# Oa15 	767.5 	2.5
# Oa16 	778.75 	15
# Oa17 	865 	20 SUN GLITTER
# Oa18 	885 	10
# Oa19 	900 	10
# Oa20 	940 	20
# Oa21 	1 020 	40

# TSM: Total Suspended Matter concentration
# CDM: Coloured Dissolved Matter
# The diffuse attenuation coefficient at 490 nm (Kd490) indicates the turbidity
# of the water column - how visible light in the blue to green region of the
# spectrum penetrates within the water column. The value of Kd490 represents
# the rate which light at 490 nm is attenuated with depth.


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


class GeoCoordinatesNotFound(IOError):
    """Error raised when the path for the geographical coordinates file does
    not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class TimeCoordinatesNotFound(IOError):
    """Error raised when the path for the temporal coordinates file does not
    exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class QualityFlagsNotFound(IOError):
    """Error raised when the path for quality flags file does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class ReflectanceFileNotFound(IOError):
    """Error raised when the path for the file which contains reflectance
    values does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class DataFileNotFound(IOError):
    """Error raised when the path for the file which contains either the
    CHL_NN, CHL_OC4ME, TSM_NN or KD490_M07 values does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ('',)
    return ('\n'.join(inp), '\t'.join(out))


def retrieve_mask_bit(quality_path: str
                      ) -> typing.Dict[str, int]:
    handler = netCDF4.Dataset(quality_path, 'r')
    bits = handler.variables['WQSF'].flag_masks
    meaning_str = handler.variables['WQSF'].flag_meanings
    handler.close()
    meanings = meaning_str.split(' ')
    mask_bits = {}
    for iflag, ibit in zip(meanings, bits):
        mask_bits[iflag] = int(numpy.log(ibit)/numpy.log(2))
    return mask_bits


def get_contrast_common_mask(quality_path: str,
                             channels: typing.List[str],
                             mask_bits: typing.Dict[str, int],
                             ) -> numpy.typing.NDArray:
    """"""
    # We keep inland waters, whitecaps
    # Allow Hisolzen flag otherwise it removes high latitude data
    off_flags = numpy.uint32(0)
    off_flags = off_flags + numpy.uint32(1 << mask_bits['INVALID'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['LAND'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['CLOUD'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['SNOW_ICE'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['COSMETIC'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['SUSPECT'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['SATURATED'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['ADJAC'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['WV_FAIL'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['PAR_FAIL'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['AC_FAIL'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['KDM_FAIL'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['CLOUD_MARGIN'])
    off_flags = off_flags + numpy.uint32(1 << mask_bits['CLOUD_AMBIGUOUS'])

    # Read quality flags
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'WQSF')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    contrast_mask = numpy.zeros(quality_flags.shape, dtype='bool')
    contrast_mask = (contrast_mask |
                     (numpy.bitwise_and(quality_flags, off_flags) > 0))

    return contrast_mask


def get_contrast_bands_mask(quality_path: str,
                            targets: typing.List[str],
                            mask_bits: typing.Dict[str, int]) -> MasksDict:
    """"""
    # Read quality flags
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'WQSF')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    masks = {}
    for var_id in targets:
        contrast_mask = numpy.zeros(quality_flags.shape, dtype='bool')

        if 'CHL_NN' == var_id:
            off_flags = numpy.uint32(0)
            off_flags = off_flags + numpy.uint32(1 << mask_bits['OCNN_FAIL'])
            contrast_mask = (contrast_mask |
                             (numpy.bitwise_and(quality_flags, off_flags) > 0))
        elif 'CHL_OC4ME' == var_id:
            off_flags = numpy.uint32(0)
            off_flags = off_flags + numpy.uint32(1 << mask_bits['OC4ME_FAIL'])
            contrast_mask = (contrast_mask |
                             (numpy.bitwise_and(quality_flags, off_flags) > 0))

        masks[var_id] = contrast_mask
    return masks


def get_dynamic_bands_mask(granule: Granule,
                           targets: typing.List[str]) -> MasksDict:
    """"""
    masks = {}
    for var_id in targets:
        var_data = granule.vars[var_id]['array']

        dyn_mask = numpy.ma.getmaskarray(var_data)
        if var_id.startswith('Oa'):
            # Mask null and negative values: they are inferior or equal to
            # atmospheric correction and should probably have been flagged as
            # clouds.
            # They should therefore not be used to computed contrast for ocean
            dyn_mask = (dyn_mask | (var_data <= 0))
        masks[var_id] = dyn_mask
    return masks


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
    variables = {'Oa04_reflectance': {'name': 'Oa04',
                                      'units': '',
                                      'valid_min': -0.02,
                                      'valid_max': 0.02,
                                      'options': {}},
                 'Oa06_reflectance': {'name': 'Oa06',
                                      'units': '',
                                      'valid_min': -0.02,
                                      'valid_max': 0.02,
                                      'options': {}},
                 'Oa09_reflectance': {'name': 'Oa09',
                                      'units': '',
                                      'valid_min': -0.02,
                                      'valid_max': 0.02,
                                      'options': {}},
                 'Oa17_reflectance': {'name': 'Oa17',
                                      'units': '',
                                      'valid_min': -0.02,
                                      'valid_max': 0.02,
                                      'options': {}},
                 'CHL_NN': {'name': 'CHL_NN',
                            'valid_min': -2.100,
                            'valid_max': 1.350,
                            'options': {}},
                 'CHL_OC4ME': {'name': 'CHL_OC4ME',
                               'valid_min': -1.700,
                               'valid_max': 1.550,
                               'options': {}},
                 'TSM_NN': {'name': 'TSM_NN',
                            'valid_min': -1.500,
                            'valid_max': 1.000,
                            'options': {}},
                 'KD490_M07': {'name': 'KD490',
                               'valid_min': -1.500,
                               'valid_max': 0.500,
                               'options': {}}}

    channels = list(variables.keys())
    visible_vars = ('Oa04_reflectance', 'Oa06_reflectance', 'Oa09_reflectance')
    infrared_vars = ('Oa17_reflectance',)
    reflectance_vars = list(visible_vars) + list(infrared_vars)
    non_reflectance_vars = ('CHL_NN', 'CHL_OC4ME', 'TSM_NN', 'KD490_M07')

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_dir = input_opts.get('path', None)
    if _input_dir is None:
        raise InputPathMissing()
    input_dir = os.path.normpath(_input_dir)

    # Check existance of required files
    geo_path = os.path.join(input_dir, 'geo_coordinates.nc')
    if not os.path.exists(geo_path):
        raise GeoCoordinatesNotFound(geo_path)

    time_path = os.path.join(input_dir, 'time_coordinates.nc')
    if not os.path.exists(time_path):
        raise TimeCoordinatesNotFound(time_path)

    quality_path = os.path.join(input_dir, 'wqsf.nc')
    if not os.path.exists(quality_path):
        raise QualityFlagsNotFound(quality_path)

    # Read variables
    for var_id in reflectance_vars:
        file_name = f'{var_id}.nc'
        file_path = os.path.join(input_dir, file_name)
        if not os.path.exists(file_path):
            raise ReflectanceFileNotFound(file_path)
        f_handler = netCDF4.Dataset(file_path, 'r')
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(band)
        granule.vars[var_id]['datatype'] = band.dtype
        f_handler.close()

    for var_id in ('CHL_NN', 'CHL_OC4ME', 'TSM_NN'):
        file_name = f'{var_id.lower()}.nc'
        file_path = os.path.join(input_dir, file_name)
        if not os.path.exists(file_path):
            raise DataFileNotFound(file_path)
        f_handler = netCDF4.Dataset(file_path, 'r')
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(band)
        granule.vars[var_id]['datatype'] = band.dtype
        f_handler.close()

    var_id = 'KD490_M07'
    file_name = 'trsp.nc'
    file_path = os.path.join(input_dir, file_name)
    if not os.path.exists(file_path):
        raise DataFileNotFound(file_path)
    f_handler = netCDF4.Dataset(file_path, 'r')
    idf_converter.lib.extract_variable_attributes(f_handler, var_id, granule)
    band = idf_converter.lib.extract_variable_values(f_handler, var_id)
    granule.vars[var_id]['array'] = numpy.ma.array(band)
    granule.vars[var_id]['datatype'] = band.dtype
    f_handler.close()

    # Extract geo coordinates information
    geo_handler = netCDF4.Dataset(geo_path, 'r')
    idf_converter.lib.extract_global_attributes(geo_handler, input_opts,
                                                granule)
    if 'title' in granule.meta.keys():
        granule.meta['title'] = granule.meta['title'].rsplit(',', 1)[0]
    nrow = geo_handler.dimensions['rows'].size
    ncell = geo_handler.dimensions['columns'].size
    lon = idf_converter.lib.extract_variable_values(geo_handler, 'longitude')
    lon = numpy.ma.array(lon)
    lat = idf_converter.lib.extract_variable_values(geo_handler, 'latitude')
    lat = numpy.ma.array(lat)
    geo_handler.close()

    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    # Handle longitude continuity
    dlon = lon[1:, :] - lon[:-1, :]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon[numpy.where(lon < 0.0)] = lon[numpy.where(lon < 0.0)] + 360.0

    # Extract time coordinates information
    time_handler = netCDF4.Dataset(time_path, 'r')
    _time = idf_converter.lib.extract_variable_values(time_handler,
                                                      'time_stamp')
    start_timestamp = _time[0]
    end_timestamp = _time[-1]
    timestamp_units = time_handler.variables['time_stamp'].units
    time_handler.close()

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = netCDF4.num2date(start_timestamp, timestamp_units)
    stop_dt = netCDF4.num2date(end_timestamp, timestamp_units)

    granule_name = os.path.basename(input_dir)

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 300
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = 'Sentinel-3'
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'OLCI'
    granule.meta['sensor_type'] = 'medium-resolution imaging spectrometer'

    # Add transforms
    transforms = []

    # Compute extrema depending on valid data proportion for reflectance bands
    # Use default values if there is not enough valid data
    # Use percentiles otherwise
    # Bands other than reflectance ones keep the default min/max
    mask_bits = retrieve_mask_bit(quality_path)
    ignored_common_mask = get_contrast_common_mask(quality_path, channels,
                                                   mask_bits)
    transforms.append(('contrast_from_pct',
                       {'targets': reflectance_vars,
                        'valid_threshold': 0.001,  # 0.1%
                        'common_mask': ignored_common_mask,
                        'bands_mask': None,
                        'dynamic_bands_mask': get_dynamic_bands_mask,
                        'min_percentile': 1.0,
                        'max_percentile': 90.0}))
    # TODO: add clipping for NIR
    # _min = numpy.clip(_min, 1.5, 10.0)
    # _max = numpy.clip(_max, 30.0, 60.0)

    # APPLY MEDIAN FILTER
    # only for non-reflectance bands
    kernels = {'CHL_NN': [3, 3],
               'CHL_OC4ME': [3, 3],
               'TSM_NN': [3, 3],
               'KD490_M07': [3, 3]}
    transforms.append(('median_filter',
                       {'targets': non_reflectance_vars,
                        'kernels': kernels}))

    # For non-reflectance bands, apply common mask
    transforms.append(('static_common_mask',
                       {'targets': non_reflectance_vars,
                        'mask': ignored_common_mask}))

    # For non-reflectance bands, also apply band-specific masks (Chl-a bands)
    ignored_bands_mask = get_contrast_bands_mask(quality_path, channels,
                                                 mask_bits)
    transforms.append(('static_bands_mask',
                       {'targets': non_reflectance_vars,
                        'masks': ignored_bands_mask}))

    output_opts['__export'] = channels

    yield input_opts, output_opts, granule, transforms
