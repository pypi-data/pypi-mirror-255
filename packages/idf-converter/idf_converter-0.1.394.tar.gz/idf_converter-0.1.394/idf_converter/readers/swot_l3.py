# vim: ts=4:sts=4:sw=4
#
# @date 2023-07-15
#
# Copyright (C) 2016-2023 OceanDataLab
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""

import os
import numpy
import numpy.typing
import typing
import logging
import netCDF4
import idf_converter.lib
from idf_converter.lib.types import ReaderResult, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'


class InputPathMissing(IOError):
    """Error raised when the "path" input option has not been provided by the
    user."""
    pass


def build_gcps(lon: numpy.typing.NDArray,
               lat: numpy.typing.NDArray,
               subsampling: typing.Optional[typing.Iterable[int]] = None
               ) -> typing.Dict[str, numpy.typing.NDArray]:
    """"""
    subsampling_s: typing.Iterable[int]
    subsampling_d: typing.Iterable[int]
    if subsampling is None:
        subsampling_s = [20, 1]
        subsampling_d = [40, 1]
    else:
        subsampling_s = subsampling
        subsampling_d = subsampling
    if numpy.ma.is_masked(lon) or numpy.ma.is_masked(lat):
        logger.warn('Some lon and/or lat is masked')

    lon_shape = numpy.array(numpy.shape(lon))  # lat should have the same shape
    x = 1
    ngcps_s = numpy.ceil(lon_shape / subsampling_s).astype('int')
    ngcps_d = numpy.ceil(lon_shape / subsampling_d).astype('int')

    len_ac = lon_shape[1] - 1
    mid_ac = int(len_ac / 2)
    gcppix = numpy.array([0, 20, 35, 36, 37, 57, 70])
    gcppix = numpy.array([0 * x, 10 * x, 20 * x, 30 * x, mid_ac - 1, mid_ac,
                          mid_ac + 1, mid_ac + 2, 40 * x, 50 * x, 60 * x,
                          len_ac])
    gcppix_s = gcppix
    ngcps_s[1] = len(gcppix_s)
    ngcps_d[1] = len(gcppix)

    gcplin_out = numpy.linspace(0, lon_shape[0] - 1,
                                num=ngcps_d[0]).round().astype('int32')
    gcplin_in = numpy.linspace(0, lon_shape[0] - 1,
                               num=ngcps_s[0]).round().astype('int32')

    gcps = {'geoloc_row': gcplin_in, 'geoloc_cell': gcppix,
            'input_row': gcplin_in, 'input_cell': gcppix,
            'output_row': gcplin_out, 'output_cell': gcppix}
    return gcps


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ''
    return ('\n'.join(inp), '\n'.join(out))


def read_data(input_opts: typing.Dict[str, typing.Any],
              output_opts: typing.Dict[str, typing.Any]
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
    variables = {'ssha': {'name': 'ssha',
                          'long_name': ('sea surface height above reference '
                                        'ellipsoid'),
                          'units': 'm',
                          'valid_min': -50.0,
                          'valid_max': 50.0,
                          'options': {}},
                 'mdt': {'name': 'mdt',
                         'long_name': 'mean dynamic topography',
                         'units': 'm',
                         'valid_min': -50.0,
                         'valid_max': 50.0,
                         'options': {}},

                 'sigma0': {'name': 'sigma0',
                            'long_name': ('normalized radar cross section '
                                          '(sigma0)'),
                            'units': 'm',
                            'valid_min': -1000.0,
                            'valid_max': 10000.0,
                            'options': {}},
                 'dac': {'name': 'dac',
                         'long_name': 'Dynamic atmospheric correction',
                         'units': 'm',
                         'valid_min': -50.0,
                         'valid_max': 50.0,
                         'options': {}},
                 'mss': {'name': 'mss',
                         'long_name': 'Mean surface slope',
                         'units': 'm',
                         'valid_min': -50.0,
                         'valid_max': 50.0,
                         'options': {}},
                 'calibration': {'name': 'calibration',
                                 'long_name': ('Instrumental Calibration '
                                               '(xover)'),
                                 'units': 'm',
                                 'valid_min': -50.0,
                                 'valid_max': 50.0,
                                 'options': {}},
                 'ssha_noiseless': {'name': 'ssha_noiseless',
                                    'long_name': ('sea surface height anomaly '
                                                  'without noise'),
                                    'units': 'm',
                                    'valid_min': -50.0,
                                    'valid_max': 50.0,
                                    'options': {}},
                 'ssha_unedited': {'name': 'ssha_unedited',
                                   'long_name': 'sea surface height anomaly',
                                   'units': 'm',
                                   'valid_min': -50.0,
                                   'valid_max': 50.0,
                                   'options': {}},
                 'quality_flag': {'name': 'quality_flag',
                                  'long_name': 'Quality flag',
                                  'units': 'm',
                                  'valid_min': 0.0,
                                  'valid_max': 1.0,
                                  'options': {}},
                 'ocean_tide': {'name': 'ocean_tide',
                                'long_name': 'Ocean tide',
                                'units': 'm',
                                'valid_min': -50.0,
                                'valid_max': 50.0,
                                'options': {}},
                 'ugos': {'name': 'ugos',
                          'long_name': ('Geostrophic Eastward component '
                                        'derived from SSH'),
                          'units': 'm',
                          'valid_min': -50.0,
                          'valid_max': 50.0,
                          'options': {}},
                 'ugosa': {'name': 'ugosa',
                           'long_name': ('Geostrophic Eastward component '
                                         'derived from SSH Anomaly'),
                           'units': 'm',
                           'valid_min': -50.0,
                           'valid_max': 50.0,
                           'options': {}},
                 'vgos': {'name': 'vgos',
                          'long_name': ('Geostrophic Northward component '
                                        'derived from SSH'),
                          'units': 'm',
                          'valid_min': -50.0,
                          'valid_max': 50.0,
                          'options': {}},
                 'vgosa': {'name': 'vgosa',
                           'long_name': ('Geostrophic Northward component '
                                         'derived from SSH Anomaly'),
                           'units': 'm',
                           'valid_min': -50.0,
                           'valid_max': 50.0,
                           'options': {}},
                 # 'wind_speed_karin': {'name': 'wind_speed_karin',
                 #              'long_name': 'wind speed from KaRIn',
                 #              'units': 'm',
                 #              'valid_min': 0.0,
                 #              'valid_max': 50.0,
                 #              'options': {}}


                 }

    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        var_ids = list(variables.keys())
    else:
        var_ids = [x.strip() for x in _var_ids.split(',')]
    channels = var_ids

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    idf_converter.lib.apply_global_overrides(input_opts, granule)
    idf_converter.lib.apply_var_overrides(input_opts, granule)
    granule.vars = {}
    maskable_channels = []
    for var_id in var_ids:
        if var_id in variables.keys():
            if 'quality_flag' != var_id:
                maskable_channels.append(var_id)
            granule.vars[var_id] = variables[var_id]
    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    qf_mask: typing.Optional[numpy.typing.NDArray] = None

    f_handler = netCDF4.Dataset(input_path, 'r')

    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)

    for var_id in granule.vars.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        values = f_handler.variables[var_id][:]
        granule.vars[var_id]['array'] = values

    # Extract geo coordinates information
    lon = f_handler.variables['longitude'][:, :]
    lat = f_handler.variables['latitude'][:, :]

    # Handle longitude continuity
    dlon = lon[1:, :] - lon[:-1, :]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon[numpy.where(lon < 0.0)] = lon[numpy.where(lon < 0.0)] + 360.0

    # Extract time coordinates information
    t = f_handler.variables['time'][:]
    t_unit = f_handler.variables['time'].units
    t_mask = numpy.ma.getmaskarray(t)
    valid_t_ind = numpy.where(~t_mask)[0]
    time = t[valid_t_ind]
    lon = lon[valid_t_ind, :]
    lat = lat[valid_t_ind, :]
    for var_id in granule.vars.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        values = f_handler.variables[var_id][valid_t_ind, :]
        granule.vars[var_id]['array'] = values

    if 'quality_flag' in f_handler.variables.keys():
        quality_flag = f_handler.variables['quality_flag'][:]
        qf = quality_flag[valid_t_ind, :]
        qf_mask = (qf == 1)
    f_handler.close()
    nrow, ncell = numpy.shape(lon)
    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = netCDF4.num2date(time[0], t_unit)
    stop_dt = netCDF4.num2date(time[-1], t_unit)

    granule_filename = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_filename)

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 2000
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    # Add transforms
    transforms: TransformsList = []

    if qf_mask is not None:
        transforms.append(('static_common_mask', {'targets': maskable_channels,
                                                  'mask': qf_mask}))

    output_opts['__export'] = channels
    output_opts['gcp_distribution'] = build_gcps(lon, lat)
    input_opts['geoloc_at_pixel_center'] = 'true'
    yield input_opts, output_opts, granule, transforms
