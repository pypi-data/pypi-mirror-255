# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-30
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
import datetime
import idf_converter.lib
from idf_converter.lib import EarlyExit
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import ReaderResult, AtmCorrData, NumValuesDict
from idf_converter.lib.types import Extrema, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'
MAX_SUNGLINT = 150.000


class InputPathMissing(IOError):
    """Error rasied when the "path" input option has not been specified by the
    user."""
    pass


class GeoCoordinatesNotFound(IOError):
    """Error raised when the path for the geographical coordinates file does
    not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class RadianceFileNotFound(IOError):
    """Error raised when the path for the file which contains radiance values
    does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class LookUpTableNotFound(IOError):
    """Error raised when the path for the lookup table file does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class TieGeometriesNotFound(IOError):
    """Error raised when the path for the tie geometries file does not exist.
    """
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class UnsupportedChannels(Exception):
    def __init__(self, channels: typing.Iterable[str],
                 *args: typing.Iterable[typing.Any]) -> None:
        _chans = ', '.join(channels)
        msg = 'The following channels are not supported: {}'.format(_chans)
        super(UnsupportedChannels, self).__init__(msg, *args)


class ChannelsMissing(Exception):
    pass


class MissingRequiredFiles(IOError):
    pass


class OnlyMaskedValues(Exception):
    pass


class OnlyNightData(Exception):
    pass


class CorruptedAtmosphericCorrection(Exception):
    def __init__(self) -> None:
        msg = ('Infinite or nan value found in the atmospheric correction, '
               'please check that the LUT has valid values for the angles '
               'contained in the geometrie_tn.nc file')
        super(CorruptedAtmosphericCorrection, self).__init__(msg)


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
    return ('\n'.join(inp), '\n'.join(out))


def fix_extrema(var_dict: typing.Dict[str, typing.Any],
                default_min: float,
                default_max: float) -> Extrema:
    """"""
    _min = var_dict['valid_min']
    _max = var_dict['valid_max']
    if 100.000 < _min:
        _min = default_min
        _max = default_max
    return _min, _max


def build_masks(input_dir: str
                ) -> typing.Tuple[numpy.typing.NDArray, numpy.typing.NDArray]:
    """"""

    bits = {'coastline': 0,
            'ocean': 1,
            'tidal': 2,
            'land': 3,
            'inland_water': 4,
            'unfilled': 5,
            'spare': 6,
            'spare_': 7,
            'cosmetic': 8,
            'duplicate': 9,
            'day': 10,
            'twilight': 11,
            'sun_glint': 12,
            'snow': 13,
            'summary_cloud': 14,
            'summary_pointing': 15}

    # Invalidate if these flags are all off
    on_flags = numpy.ushort(0)
    on_flags = on_flags + numpy.ushort(1 << bits['day'])

    # Invalidate if any of these flags is on
    off_flags = numpy.ushort(0)
    off_flags = off_flags + numpy.ushort(1 << bits['coastline'])
    off_flags = off_flags + numpy.ushort(1 << bits['land'])
    off_flags = off_flags + numpy.ushort(1 << bits['snow'])

    # Read quality flags
    quality_path = os.path.join(input_dir, 'flags_an.nc')
    quality_handler = netCDF4.Dataset(quality_path, 'r')
    _quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                               'confidence_an')
    quality_flags = numpy.ma.array(_quality_flags)
    quality_handler.close()

    # Intialize mask to compute histograms on selected valid values
    contrast_mask = numpy.zeros(quality_flags.shape, dtype='bool')

    # Initialize mask to remove invalid data
    data_mask = numpy.zeros(quality_flags.shape, dtype='bool')

    # Mask data under sun_glint too
    off_flags = off_flags + numpy.uint32(1 << bits['sun_glint'])

    contrast_mask = (contrast_mask |
                     (numpy.bitwise_and(quality_flags, on_flags) <= 0) |
                     (numpy.bitwise_and(quality_flags, off_flags) > 0))

    # Granules containing only night/twilight data must be ignored.
    # Twilight data are only useful to improve the contrast when there is
    # at least some daily data.
    on_flags = numpy.ushort(0)
    on_flags |= numpy.ushort(1 << bits['day'])
    data_mask = (data_mask |
                 (numpy.bitwise_and(quality_flags,  on_flags) <= 0))
    if data_mask.all():
        raise OnlyNightData()

    return contrast_mask, data_mask


def get_bands_contrast_mask(granule: Granule,
                            targets: typing.List[str]) -> NumValuesDict:
    """"""
    masks = {}
    for var_id in targets:
        var_data = granule.vars[var_id]['array']

        # Ignore sunglint when computing the contrast for RGB channels
        sunglint_mask = (var_data >= MAX_SUNGLINT)
        negative_mask = (var_data <= 0)
        data_mask = (numpy.ma.getmaskarray(var_data))
        masks[var_id] = (data_mask | negative_mask | sunglint_mask)

    return masks


def get_atm_corr_data(input_dir: str, lut_path: str,
                      nrow: int, ncell: int) -> AtmCorrData:
    """"""
    view = 'n'  # Nadir view

    if not os.path.exists(lut_path):
        raise LookUpTableNotFound(lut_path)

    tie_geometries_path = os.path.join(input_dir, f'geometry_t{view}.nc')
    if not os.path.exists(tie_geometries_path):
        raise TieGeometriesNotFound(tie_geometries_path)

    bands_count = 9  # S1 -> S9

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

    # Bands numbering starts at 1 and are name "S_" where _ is the band
    # number
    bands_index = {f'S{x + 1}_radiance_an': x for x in range(0, bands_count)}

    # Read angles from geometry_t*.nc
    f_handler = netCDF4.Dataset(tie_geometries_path, 'r')
    sza = idf_converter.lib.extract_variable_values(f_handler,
                                                    f'solar_zenith_t{view}')
    saa = idf_converter.lib.extract_variable_values(f_handler,
                                                    f'solar_azimuth_t{view}')
    oaa = idf_converter.lib.extract_variable_values(f_handler,
                                                    f'sat_azimuth_t{view}')
    oza = idf_converter.lib.extract_variable_values(f_handler,
                                                    f'sat_zenith_t{view}')
    f_handler.close()

    # if sza is more than 90 take values from 80 - 85 range
    sza_nan_ind = numpy.where(numpy.isnan(sza))
    sza[sza_nan_ind] = -1  # temporary, to avoid warnings with "sza > 84"
    sza[sza > 84] = 84
    sza[sza_nan_ind] = numpy.nan

    # Replace nan values by the last valid one
    ifirst = 19
    ilast = ifirst + 1
    sza[:, -ifirst:] = numpy.repeat(sza[:, -ilast],
                                    ifirst).reshape((sza.shape[0], ifirst))
    saa[:, -ifirst:] = numpy.repeat(saa[:, -ilast],
                                    ifirst).reshape((saa.shape[0], ifirst))
    oza[:, -ifirst:] = numpy.repeat(oza[:, -ilast],
                                    ifirst).reshape((oza.shape[0], ifirst))
    oaa[:, -ifirst:] = numpy.repeat(oaa[:, -ilast],
                                    ifirst).reshape((oaa.shape[0], ifirst))

    # Read Extra-terrestrial solar irradiance
    solar_flux = {}
    _get_values = idf_converter.lib.extract_variable_values
    for band_index in range(0, bands_count):
        band_number = band_index + 1
        band_name = f'S{band_number}_radiance_an'
        if band_index > 5:  # band_index = 6 <=> band_name = S7
            continue
        file_name = f'S{band_number}_quality_an.nc'
        file_path = os.path.join(input_dir, file_name)
        f_handler = netCDF4.Dataset(file_path, 'r')
        var_name = f'S{band_number}_solar_irradiance_an'
        solar_flux[band_name] = _get_values(f_handler, var_name)
        f_handler.close()

    nrow_geom, ncell_geom = numpy.shape(sza)
    if abs(nrow_geom - nrow / 2.0) > 1:
        logger.warning('Discrepency between channel and geometry dimensions')

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
                     'al_subsampled': True,
                     'ac_subsampling': int(ncell / ncell_geom)}

    return atm_corr_data


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
    variables = {'S1_radiance_an': {'name': 'S1',
                                    'valid_min': 14.000,
                                    'valid_max': 150.000,
                                    'options': {}},
                 'S2_radiance_an': {'name': 'S2',
                                    'valid_min': 8.000,
                                    'valid_max': 150.000,
                                    'options': {}},
                 'S3_radiance_an': {'name': 'S3',
                                    'valid_min': 4.000,
                                    'valid_max': 150.000,
                                    'options': {}}}

    channels = list(variables.keys())

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_dir = input_opts.get('path', None)
    input_dir = os.path.normpath(_input_dir)
    if input_dir is None:
        raise InputPathMissing()

    view = 'n'  # Process nadir view
    sltype = 'a'

    # Check existance of required files
    geo_path = os.path.join(input_dir, f'geodetic_{sltype}{view}.nc')
    if not os.path.exists(geo_path):
        raise GeoCoordinatesNotFound(geo_path)

    atm_corr_lut_path = input_opts.get('atmospheric_correction_LUT_path', None)
    atm_correction_requested = atm_corr_lut_path is not None

    # Read variables
    for var_id in channels:
        file_name = f'{var_id}.nc'
        rad_path = os.path.join(input_dir, file_name)
        if not os.path.exists(rad_path):
            raise RadianceFileNotFound(rad_path)

        f_handler = netCDF4.Dataset(rad_path, 'r')
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(band)
        f_handler.close()

        band_mask = numpy.ma.getmaskarray(granule.vars[var_id]['array'])
        if numpy.all(band_mask):
            logger.warning(f'All values masked for channel {var_id}')

    # Extract geo coordinates information
    lat_varname = 'latitude_{}{}'.format(sltype, view)
    lon_varname = 'longitude_{}{}'.format(sltype, view)
    geo_handler = netCDF4.Dataset(geo_path, 'r')
    idf_converter.lib.extract_global_attributes(geo_handler, input_opts,
                                                granule)
    nrow = geo_handler.dimensions['rows'].size
    ncell = geo_handler.dimensions['columns'].size
    lon = idf_converter.lib.extract_variable_values(geo_handler, lon_varname)
    lon = numpy.ma.array(lon)
    lat = idf_converter.lib.extract_variable_values(geo_handler, lat_varname)
    lat = numpy.ma.array(lat)
    start_time_str = geo_handler.start_time
    stop_time_str = geo_handler.stop_time
    geo_handler.close()

    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    # Handle longitude continuity
    dlon = lon[1:, :] - lon[:-1, :]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon0 = lon[0, 0] + 180.0
        lon[:, :] = numpy.mod(lon[:, :] - lon0, 360.0) + lon0

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    time_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
    start_dt = datetime.datetime.strptime(start_time_str, time_fmt)
    stop_dt = datetime.datetime.strptime(stop_time_str, time_fmt)

    granule_name = os.path.basename(input_dir)

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 500
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = 'Sentinel-3'
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'SLSTR'
    granule.meta['sensor_type'] = 'dual scan temperature radiometer'

    # Add transforms
    transforms: TransformsList = []

    # APPLY ATMOSPHERIC CORRECTION
    if atm_correction_requested:
        atm_corr_data = get_atm_corr_data(input_dir, atm_corr_lut_path, nrow,
                                          ncell)
        transforms.append(('s3_cnes_rayleigh',
                           {'targets': channels,
                            'atm_corr_data': atm_corr_data}))

    # Compute extrema depending on valid data proportion
    # Use default values if there is not enough valid data
    # Use percentiles otherwise
    try:
        ignored_mask, data_mask = build_masks(input_dir)
    except OnlyNightData:
        logger.warning('No day data in granule, the IDF would only contain '
                       'masked values. Exiting')
        raise EarlyExit()

    transforms.append(('contrast_from_pct',
                       {'targets': channels,
                        'valid_threshold': 0.001,  # 0.1%
                        'common_mask': ignored_mask,
                        'bands_mask': None,
                        'dynamic_bands_mask': get_bands_contrast_mask,
                        'min_percentile': 2.0,
                        'max_percentile': 99.99}))

    # Make sure max never exceeds the maximum sun glint
    transforms.append(('limit_extrema', {'targets': channels,
                                         'max_threshold': MAX_SUNGLINT}))

    # take default min and max if min is too high (lake, inland sea, clouds)
    #
    # At this point in the code, valid_min and valid_max have not been modified
    # so they are still the default values
    minmax_methods = {var_id: fix_extrema for var_id in channels}
    min_values = {var_id: v['valid_min'] for var_id, v in granule.vars.items()
                  if var_id in channels}
    max_values = {var_id: v['valid_max'] for var_id, v in granule.vars.items()
                  if var_id in channels}
    transforms.append(('extrema_methods', {'targets': channels,
                                           'methods': minmax_methods,
                                           'min_values': min_values,
                                           'max_values': max_values}))

    # Mask night data.
    transforms.append(('static_common_mask', {'targets': channels,
                                              'mask': data_mask}))

    # Share extrema among visible channels
    # TODO: remove this when SEAScope includes a way to configure channels
    # independently in RGB rendering
    transforms.append(('share_extrema', {'targets': channels}))

    # APPLY LOGARITHMIC SCALE
    # Pixels with a radiance equal or inferior to atmospheric correction
    # will be clipped to the minimal value as logscale cannot be applied to
    # negative values.
    transforms.append(('logscale', {'targets': channels,
                                    'base': 0}))

    output_opts['__export'] = channels

    yield input_opts, output_opts, granule, transforms
