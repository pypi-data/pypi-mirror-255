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
import numpy.typing
import typing
import netCDF4
import logging
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import ReaderResult, AtmCorrData, NumValuesDict
from idf_converter.lib.types import TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'
MASK_BITS = {'saturated@Oa21': 0,
             'saturated@Oa20': 1,
             'saturated@Oa19': 2,
             'saturated@Oa18': 3,
             'saturated@Oa17': 4,
             'saturated@Oa16': 5,
             'saturated@Oa15': 6,
             'saturated@Oa14': 7,
             'saturated@Oa13': 8,
             'saturated@Oa12': 9,
             'saturated@Oa11': 10,
             'saturated@Oa10': 11,
             'saturated@Oa09': 12,
             'saturated@Oa08': 13,
             'saturated@Oa07': 14,
             'saturated@Oa06': 15,
             'saturated@Oa05': 16,
             'saturated@Oa04': 17,
             'saturated@Oa03': 18,
             'saturated@Oa02': 19,
             'saturated@Oa01': 20,
             'dubious': 21,
             'sun-glint_risk': 22,
             'duplicated': 23,
             'cosmetic': 24,
             'invalid': 25,
             'straylight_risk': 26,
             'bright': 27,
             'tidal_region': 28,
             'fresh_inland_water': 29,
             'coastline': 30,
             'land': 31}

# S-2 : 665, 560, 490
# red : 650 nm
# green : 510 nm
# blue : 475 nm
# https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-olci/overview/heritage
# https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-olci/level-1/fr-or-rr-toa-radiances
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


class InputPathMissing(IOError):
    """"""
    pass


class GeoCoordinatesNotFound(IOError):
    """"""
    pass


class TimeCoordinatesNotFound(IOError):
    """"""
    pass


class QualityFlagsNotFound(IOError):
    """"""
    pass


class RadianceFileNotFound(IOError):
    """"""
    pass


class TieGeometriesNotFound(IOError):
    """"""
    pass


class InstrumentDataNotFound(IOError):
    """"""
    pass


class LookUpTableNotFound(IOError):
    """"""
    pass


class IncompatibleGeometryDetected(ValueError):
    """Error raised when the alongtrack dimension in the tie geometry file
    differs from the alongtrack dimension of the geo coordinates file."""
    pass


def get_brightness_mask(quality_path: str
                        ) -> numpy.typing.NDArray:
    """"""
    off_invalid = numpy.uint32(1 << MASK_BITS['invalid'])
    off_fresh = numpy.uint32(1 << MASK_BITS['fresh_inland_water'])
    off_land = numpy.uint32(1 << MASK_BITS['land'])

    # Read quality flags
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'quality_flags')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    mask: numpy.typing.NDArray
    mask = ((numpy.bitwise_and(quality_flags, off_invalid) > 0) |
            ((numpy.bitwise_and(quality_flags, off_land) > 0) &
             (numpy.bitwise_and(quality_flags, off_fresh) == 0)))

    return mask


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           '    atmospheric_correction_LUT_path\tPath of the Rayleigh'
           ' scattering LUT (CNES)')
    out = ('',)
    return ('\n'.join(inp), '\t'.join(out))


def get_contrast_common_mask(quality_path: str,
                             channels: typing.Iterable[str]
                             ) -> numpy.typing.NDArray:
    """"""
    off_flags = numpy.uint32(0)
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['dubious'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['invalid'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['straylight_risk'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['bright'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['tidal_region'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['coastline'])
    off_flags = off_flags + numpy.uint32(1 << MASK_BITS['land'])

    # We keep inland waters
    # off_flags += numpy.uint32(1 << bits['fresh_inland_water'])

    # Read quality flags
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'quality_flags')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    contrast_mask = numpy.zeros(quality_flags.shape, dtype='bool')
    contrast_mask = (contrast_mask |
                     (numpy.bitwise_and(quality_flags, off_flags) > 0))
    return contrast_mask


def get_contrast_bands_mask(quality_path: str,
                            channels: typing.Iterable[str]) -> NumValuesDict:
    """"""
    # Read quality flags
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'quality_flags')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    # Filter out values where any of the bands is flagged as saturated
    masks = {}
    for band_name in channels:
        bit_name = 'saturated@{}'.format(band_name[0:4])
        off_flags = numpy.uint32(0)
        off_flags = off_flags + numpy.uint32(1 << MASK_BITS[bit_name])

        _mask = numpy.zeros(quality_flags.shape, dtype='bool')
        _mask = (_mask | (numpy.bitwise_and(quality_flags, off_flags) > 0))
        masks[band_name] = _mask
    return masks


def get_atm_corr_data(input_dir: str, lut_path: str,
                      nrow: int, ncell: int) -> AtmCorrData:
    """"""
    if not os.path.exists(lut_path):
        raise LookUpTableNotFound(lut_path)

    instrument_path = os.path.join(input_dir, 'instrument_data.nc')
    if not os.path.exists(instrument_path):
        raise InstrumentDataNotFound(instrument_path)

    tie_geometries_path = os.path.join(input_dir, 'tie_geometries.nc')
    if not os.path.exists(tie_geometries_path):
        raise TieGeometriesNotFound(tie_geometries_path)

    bands_count = 21  # Oa01 -> Oa21

    # Read Look-Up Table
    sza_lut = []
    oza_lut = []
    delta_lut = []
    rho_atm = []
    with open(lut_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            split_line = line.split(' ')
            sza_lut.append(split_line[0])
            oza_lut.append(split_line[1])
            delta_lut.append(split_line[2])
            rho_line = []
            for icolband in range(3, 3 + bands_count):
                rho_line.append(float(split_line[icolband]))
            rho_atm.append(rho_line)

    # Bands numbering starts at 1 and are name "Oa__" where __ is the band
    # number (2 digits)
    bands_index = {f'Oa{x + 1:02}_radiance': x for x in range(0, bands_count)}

    # Read angles from tie_geometries.nc
    f_handler = netCDF4.Dataset(tie_geometries_path, 'r')
    sza = idf_converter.lib.extract_variable_values(f_handler, 'SZA')
    saa = idf_converter.lib.extract_variable_values(f_handler, 'SAA')
    oaa = idf_converter.lib.extract_variable_values(f_handler, 'OAA')
    oza = idf_converter.lib.extract_variable_values(f_handler, 'OZA')
    ac_subsampling = f_handler.ac_subsampling_factor
    f_handler.close()

    nrow_geom, ncell_geom = numpy.shape(sza)
    if nrow_geom != nrow:
        raise IncompatibleGeometryDetected()

    # Read Extra-terrestrial solar irradiance
    solar_flux = {}
    f_handler = netCDF4.Dataset(instrument_path, 'r')
    _solar_flux = idf_converter.lib.extract_variable_values(f_handler,
                                                            'solar_flux')
    for band_index in range(0, bands_count):
        band_name = f'Oa{band_index + 1:02}_radiance'
        solar_flux[band_name] = numpy.ma.array(_solar_flux[band_index])
    f_handler.close()

    atm_corr_data = {'SZA_LUT': sza_lut,
                     'OZA_LUT': oza_lut,
                     'DELTA_LUT': delta_lut,
                     'RHO_LUT': rho_atm,
                     'bands_count': bands_count,
                     'bands_index': bands_index,
                     'nrow': nrow,
                     'ncell': ncell,
                     'SZA': numpy.ma.array(sza),
                     'SAA': numpy.ma.array(saa),
                     'OAA': numpy.ma.array(oaa),
                     'OZA': numpy.ma.array(oza),
                     'solar_flux': solar_flux,
                     'al_subsampled': False,
                     'ac_subsampling': ac_subsampling}

    return atm_corr_data


def get_dynamic_bands_mask(granule: Granule,
                           targets: typing.List[str]) -> NumValuesDict:
    """"""
    masks = {}
    for var_id in targets:
        var_data = granule.vars[var_id]['array']

        # Mask null and negative values: they are inferior or equal to
        # atmospheric correction and should probably have been flagged as
        # clouds.
        # They should therefore not be used to computed contrast for ocean
        masks[var_id] = (numpy.ma.getmaskarray(var_data) |
                         (var_data <= 0))
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
    variables = {'Oa04_radiance': {'name': 'Oa04',
                                   'valid_min': 13.966,
                                   'valid_max': 95.000,
                                   'options': {}},
                 'Oa06_radiance': {'name': 'Oa06',
                                   'valid_min': 8.213,
                                   'valid_max': 95.000,
                                   'options': {}},
                 'Oa09_radiance': {'name': 'Oa09',
                                   'valid_min': 3.346,
                                   'valid_max': 95.000,
                                   'options': {}},
                 'Oa17_radiance': {'name': 'Oa17',
                                   'valid_min': 3.000,
                                   'valid_max': 150.000,
                                   'options': {}},
                 'Oa17_radiance_bc': {'name': 'Oa17_bc',
                                      'long_name': ('Brightness contrast for '
                                                    'OLCI acquisition band '
                                                    'Oa17'),
                                      'units': '',
                                      'valid_min': numpy.exp(-1.2),
                                      'valid_max': numpy.exp(1.5),
                                      'options': {}}}

    visible_vars = ('Oa04_radiance', 'Oa06_radiance', 'Oa09_radiance')
    infrared_vars = ('Oa17_radiance',)
    radiance_vars = ('Oa04_radiance', 'Oa06_radiance', 'Oa09_radiance',
                     'Oa17_radiance')
    channels = list(radiance_vars)

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

    quality_path = os.path.join(input_dir, 'qualityFlags.nc')
    if not os.path.exists(quality_path):
        raise QualityFlagsNotFound(quality_path)

    atm_corr_lut_path = input_opts.get('atmospheric_correction_LUT_path', None)
    atm_correction_requested = atm_corr_lut_path is not None

    compute_nir_nb = True

    # Read variables
    for var_id in radiance_vars:
        file_name = f'{var_id}.nc'
        radiance_path = os.path.join(input_dir, file_name)
        if not os.path.exists(radiance_path):
            raise RadianceFileNotFound(radiance_path)

        f_handler = netCDF4.Dataset(radiance_path, 'r')
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(band)
        granule.vars[var_id]['datatype'] = band.dtype
        f_handler.close()

    # Extract geo coordinates information
    geo_handler = netCDF4.Dataset(geo_path, 'r')
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
        lon[lon < 0.0] = lon[lon < 0.0] + 360.0

    # Extract time coordinates information
    time_handler = netCDF4.Dataset(time_path, 'r')
    idf_converter.lib.extract_global_attributes(time_handler, input_opts,
                                                granule)
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
    transforms: TransformsList = []

    # APPLY ATMOSPHERIC CORRECTION
    if atm_correction_requested:
        atm_corr_data = get_atm_corr_data(input_dir, atm_corr_lut_path, nrow,
                                          ncell)

        # Add brightness contrast
        if compute_nir_nb:
            bc_mask = get_brightness_mask(quality_path)

            transforms.append(('s3_nir_bc', {'targets': infrared_vars,
                                             'atm_corr_data': atm_corr_data}))

            bc_channels = [f'{channel}_bc' for channel in infrared_vars]
            transforms.append(('static_common_mask', {'targets': bc_channels,
                                                      'mask': bc_mask}))
            channels.extend(bc_channels)

        transforms.append(('s3_cnes_rayleigh',
                           {'targets': radiance_vars,
                            'atm_corr_data': atm_corr_data}))

    # Compute extrema depending on valid data proportion
    # Use default values if there is not enough valid data
    # Use percentiles otherwise
    ignored_common_mask = get_contrast_common_mask(quality_path,
                                                   radiance_vars)
    ignored_bands_mask = get_contrast_bands_mask(quality_path,
                                                 radiance_vars)
    transforms.append(('contrast_from_pct',
                       {'targets': radiance_vars,
                        'valid_threshold': 0.001,  # 0.1%
                        'common_mask': ignored_common_mask,
                        'bands_mask': ignored_bands_mask,
                        'dynamic_bands_mask': get_dynamic_bands_mask,
                        'min_percentile': 0.5,
                        'max_percentile': 99.99}))

    # Share extrema among visible channels
    transforms.append(('share_extrema', {'targets': visible_vars}))

    # Artificially increase the range on a linear scale, thus allowing
    # users to desaturate the rendering of this channel in SEAScope
    # _max_linear = _min_linear + 5 * (_max_linear - _min_linear)
    transforms.append(('stretch_extent', {'targets': radiance_vars,
                                          'stretch_factor': 5.0,
                                          'change_vmin': False,
                                          'change_vmax': True}))

    # APPLY LOGARITHMIC SCALE
    # Pixels with a radiance equal or inferior to atmospheric correction
    # will be clipped to the minimal value as logscale cannot be applied to
    # negative values.
    transforms.append(('logscale', {'targets': channels,
                                    'base': 0}))

    # TODO: it was necessary for Syntool but is it relevant for SEAScope?
    # transforms.append(('share_masks', {'targets': channels}))

    output_opts['__export'] = channels

    yield input_opts, output_opts, granule, transforms
