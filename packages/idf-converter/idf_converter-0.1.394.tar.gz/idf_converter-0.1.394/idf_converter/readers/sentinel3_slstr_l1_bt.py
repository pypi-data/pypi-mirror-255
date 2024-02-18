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
https://earth.esa.int/web/sentinel/technical-guides/sentinel-3-slstr/level-1/vis-and-swir-radiances
https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-slstr/data-formats/level-1
https://earth.esa.int/web/sentinel/user-guides/sentinel-3-slstr/product-types/level-1b
https://sentinel.esa.int/documents/247904/685236/Sentinel-3_User_Handbook#%5B%7B%22num%22%3A235%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C54%2C628%2C0%5D

S1 555   nm            B
S2 659   nm            G
S3 865   nm            R
S4 1.375 microm
S5 1.610 microm
S6 2.25  microm
S7 3.74  microm        IR
S8 10.85 microm        IR
S9 12    microm        IR
"""

import os
import numpy
import numpy.typing
import typing
import netCDF4
import logging
import datetime
import scipy.ndimage
import defusedxml.ElementTree as ET
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions
from idf_converter.lib.types import ReaderResult, FormatterJob

logger = logging.getLogger(__name__)

N2SSTInputs = typing.Tuple[typing.Dict[str, typing.Any], numpy.ndarray]
CloudBitsToMask002 = typing.Tuple[str, str, str, str, str, str, str]
CloudBitsToMask003 = typing.Tuple[str, str, str, str, str, str, str, str, str,
                                  str, str, str]
DATA_MODEL = 'SWATH'


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


class BrightnessTemperatureFileNotFound(IOError):
    """Error raised when the path for the file which contains brightness
    temperature values does not exist."""
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class SSTCoefficientsPathNotFound(IOError):
    """Error raised when the path for the SST coefficients file does not exist.
    """
    def __init__(self, path: str) -> None:
        """"""
        self.path = path


class BaselineNotSupported(Exception):
    """Error raised when the input file corresponds to a product version which
    is either not supported or has not been properly tested with this reader.
    """
    def __init__(self, baseline: str) -> None:
        """"""
        self.baseline = baseline


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


def read_manifest(input_dir: str) -> typing.Dict[str, typing.Any]:
    """ Read metadata in xml file. Return start and track Offset, number of
    lines and elements spatial resolution for Tie Points, 1 km nadir and 1 km
    oblique grid."""
    nfile = os.path.join(input_dir, 'xfdumanifest.xml')
    tree = ET.parse(nfile)
    root = tree.getroot()
    param = {}
    s3path = '{http://www.esa.int/safe/sentinel/sentinel-3/1.0}'
    slstrpath = '{http://www.esa.int/safe/sentinel/sentinel-3/slstr/1.0}'
    for a_child in root.findall("./*/metadataObject/metadataWrap/xmlData/*"):
        for child in a_child:
            if child.tag == '{}nadirImageSize'.format(slstrpath):
                if child.attrib['grid'] == '1 km':
                    for item in child.findall("./*"):
                        if item.tag == '{}startOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['startOffset_n'] = float(_item)
                        if item.tag == '{}trackOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['trackOffset_n'] = float(_item)
                        if item.tag == '{}rows'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['line_n'] = int(_item)
                        if item.tag == '{}columns'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['elem_n'] = int(_item)
                if child.attrib['grid'] == 'Tie Points':
                    for item in child.findall("./*"):
                        if item.tag == '{}startOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['startOffset_tx'] = float(_item)
                        if item.tag == '{}trackOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['trackOffset_tx'] = float(_item)
                        if item.tag == '{}rows'.format(s3path):
                            param['line_tx'] = int(item.text.encode('utf8'))
                        if item.tag == '{}columns'.format(s3path):
                            param['elem_tx'] = int(item.text.encode('utf8'))
            if child.tag == '{}obliqueImageSize'.format(slstrpath):
                if child.attrib['grid'] == '1 km':
                    for item in child.findall("./*"):
                        if item.tag == '{}startOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['startOffset_o'] = float(_item)
                        if item.tag == '{}trackOffset'.format(s3path):
                            _item = item.text.encode('utf8')
                            param['trackOffset_o'] = float(_item)
                        if item.tag == '{}rows'.format(s3path):
                            param['line_o'] = int(item.text.encode('utf8'))
                        if item.tag == '{}columns'.format(s3path):
                            param['elem_o'] = int(item.text.encode('utf8'))
            if child.tag == '{}resolution'.format(slstrpath):
                if child.attrib['grid'] == '1 km':
                    for item in child.findall("./*"):
                        if item.tag == '{}spatialResolution'.format(slstrpath):
                            param['res_n'] = float(item.text.encode('utf8'))
                if child.attrib['grid'] == 'Tie Points':
                    for item in child.findall("./*"):
                        if item.tag == '{}spatialResolution'.format(slstrpath):
                            param['res_tx'] = float(item.text.encode('utf8'))
            if child.tag == f'{s3path}baselineCollection':
                param['baselineCollection'] = child.text.encode('utf-8')
    return param


def get_n2_sst_inputs(input_dir: str, coeff_path: str) -> N2SSTInputs:
    """"""
    param = read_manifest(input_dir)

    quality_flags_path = os.path.join(input_dir, 'flags_in.nc')
    quality_handler = netCDF4.Dataset(quality_flags_path, 'r')
    quality_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                              'confidence_in')
    cloud_flags = idf_converter.lib.extract_variable_values(quality_handler,
                                                            'cloud_in')
    quality_handler.close()

    # INFRARED MASK
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

    ir_mask = (numpy.bitwise_and(quality_flags, off_flags) > 0)

    # CLOUD MASK
    cloud_bits = {'visible': 0,
                  'threshold': 1,
                  'small_histogram1.6': 2,
                  'large_histogram1.6': 3,
                  'small_histogram2.25': 4,
                  'large_histogram2.25': 5,
                  'spatial_coherence': 6,
                  'gross_cloud': 7,
                  'thin_cirrus': 8,
                  'medium_high': 9,
                  'fog_low_stratus': 10,
                  '11_12_view_difference': 11,
                  '3.7_11_view_difference': 12,
                  'thermal_histogram': 13}

    collection = param['baselineCollection']
    cloud_bits_to_mask: typing.Union[CloudBitsToMask002, CloudBitsToMask003]
    if collection == b'002':
        cloud_bits_to_mask = ('visible',
                              'threshold',
                              # 'small_histogram1.6',
                              # 'small_histogram2.25',
                              'spatial_coherence',
                              'gross_cloud',
                              'thin_cirrus',
                              'medium_high',
                              'fog_low_stratus',
                              # '11_12_view_difference',
                              )
    elif collection in (b'003', b'004'):
        cloud_bits_to_mask = ('visible',
                              'threshold',
                              'small_histogram1.6',
                              'large_histogram1.6',
                              'small_histogram2.25',
                              'large_histogram2.25',
                              'spatial_coherence',
                              'gross_cloud',
                              'thin_cirrus',
                              'medium_high',
                              'fog_low_stratus',
                              '11_12_view_difference',
                              # '3.7_11_view_difference',
                              )
    else:
        logger.error('Baseline collection should be 002, 003 or 004')
        raise BaselineNotSupported(collection)

    mask_ref = numpy.ushort(0)
    mask_spatial = numpy.ushort(0)
    # Enable selected mask bits
    for mask_name in cloud_bits_to_mask:
        if mask_name == 'spatial_coherence':
            mask_spatial = mask_spatial + (1 << cloud_bits[mask_name])
        else:
            mask_ref = mask_ref + (1 << cloud_bits[mask_name])

    # Build cloud mask
    _cloud_mask = numpy.zeros(shape=cloud_flags.shape, dtype='bool')
    _cloud_mask = (_cloud_mask |
                   (numpy.bitwise_and(cloud_flags, mask_spatial) > 1) |
                   (numpy.bitwise_and(cloud_flags, mask_ref) > 1))

    binary_dilation = scipy.ndimage.binary_dilation

    # Dilate non-masked data
    dil_kern = numpy.ones((9, 9), dtype='bool')
    cloud_mask_dil = ~(binary_dilation(~_cloud_mask, structure=dil_kern))

    # Erode cloud mask
    dil_kern = numpy.ones((9, 9), dtype='bool')
    cloud_mask = (binary_dilation(cloud_mask_dil, structure=dil_kern))
    cloud_mask = (cloud_mask |
                  (numpy.bitwise_and(cloud_flags, mask_ref) > 1))

    # -------------------------------------------------------------------------
    # Do not mask data at night or twilight for ir channels.
    data_mask = numpy.zeros(quality_flags.shape, dtype='bool')
    data_mask = (data_mask | cloud_mask | ir_mask)

    # - Get satellite angles
    nfile = os.path.join(input_dir, 'geometry_tn.nc')
    fid = netCDF4.Dataset(nfile, 'r')
    sat_zen_n = idf_converter.lib.extract_variable_values(fid, 'sat_zenith_tn')
    fid.close()

    # - Get TCWV from MET file
    nfile = os.path.join(input_dir, 'met_tx.nc')
    fid = netCDF4.Dataset(nfile, 'r')
    tcwv_var_id = 'total_column_water_vapour_tx'
    _tcwv = idf_converter.lib.extract_variable_values(fid, tcwv_var_id)
    tcwv = _tcwv[0, :, :]
    fid.close()

    # -- Read SST coefficents for nadir
    fid = netCDF4.Dataset(coeff_path, 'r')
    coeffs_n2 = idf_converter.lib.extract_variable_values(fid,
                                                          'coefficients_LUT')
    fid.close()

    n2_sst_inputs = {'tcwv': tcwv,
                     'sat_zen_n': sat_zen_n,
                     'param': param,
                     'coeffs_n2': coeffs_n2,
                     'n11_id': 'S8_BT_in',
                     'n12_id': 'S9_BT_in'}
    return n2_sst_inputs, data_mask


def get_sst_mask(variables: typing.Dict[str, typing.Dict[str, typing.Any]],
                 var_id: str
                 ) -> numpy.typing.NDArray:
    """"""
    n11_mask = numpy.ma.getmaskarray(variables['S8_BT_in']['array'])
    n12_mask = numpy.ma.getmaskarray(variables['S9_BT_in']['array'])
    result: numpy.typing.NDArray = (n11_mask | n12_mask)
    return result


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

    variables = {'S7_BT_in': {'name': 'S7',
                              'valid_min': 220.000,
                              'valid_max': 310.000,
                              'options': {}},
                 'S8_BT_in': {'name': 'S8',
                              'valid_min': 197.400,
                              'valid_max': 306.000,
                              'options': {}},
                 'S9_BT_in': {'name': 'S9',
                              'valid_min': 190.150,
                              'valid_max': 306.150,
                              'options': {}},
                 'sst': {'name': 'sea_surface_temperature',
                         'long_name': 'Sea surface temperature',
                         'units': 'K',
                         'valid_min': 270.15,
                         'valid_max': 310.15,
                         'options': {}}}

    radiance_vars = ['S7_BT_in', 'S8_BT_in', 'S9_BT_in']

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_dir = input_opts.get('path', None)
    if _input_dir is None:
        raise InputPathMissing()
    input_dir = os.path.normpath(_input_dir)

    sst_coeffs_path = input_opts.get('sst_coeffs_path', None)
    if sst_coeffs_path is None:
        del variables['sst']
    elif not os.path.exists(sst_coeffs_path):
        raise SSTCoefficientsPathNotFound(sst_coeffs_path)

    # Check existance of required files
    geo_path = os.path.join(input_dir, 'geodetic_in.nc')
    if not os.path.exists(geo_path):
        raise GeoCoordinatesNotFound(geo_path)

    # Read variables
    for var_id in radiance_vars:
        file_name = f'{var_id}.nc'
        bt_path = os.path.join(input_dir, file_name)
        if not os.path.exists(bt_path):
            raise BrightnessTemperatureFileNotFound(bt_path)

        f_handler = netCDF4.Dataset(bt_path, 'r')
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(band)
        f_handler.close()

        band_mask = numpy.ma.getmaskarray(variables[var_id]['array'])
        if numpy.all(band_mask):
            logger.warning(f'All values masked for channel {var_id}')

    # Extract geo coordinates information
    lat_varname = 'latitude_in'
    lon_varname = 'longitude_in'
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
    granule.meta['idf_spatial_resolution'] = 1000  # 1km
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = 'Sentinel-3'
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'SLSTR'
    granule.meta['sensor_type'] = 'dual scan temperature radiometer'

    # Add transforms
    transforms = []

    channels = ['S7_BT_in', 'S8_BT_in', 'S9_BT_in']
    if sst_coeffs_path:
        n2_sst_inputs, data_mask = get_n2_sst_inputs(input_dir,
                                                     sst_coeffs_path)
        transforms.append(('n2_sst_from_slstr', {'input_data': n2_sst_inputs}))

        # mask night data for rgb and invalid data for ir (cloud, land,
        # range value).
        night_mask_job: FormatterJob = ('static_common_mask',
                                        {'targets': ['sst'],
                                         'mask': data_mask})
        transforms.append(night_mask_job)

        sst_dyn_mask = {'sst': get_sst_mask}
        sst_input_mask_job: FormatterJob = ('mask_methods',
                                            {'targets': ['sst'],
                                             'methods': sst_dyn_mask})
        transforms.append(sst_input_mask_job)

        channels.append('sst')

    output_opts['__export'] = channels

    yield input_opts, output_opts, granule, transforms
