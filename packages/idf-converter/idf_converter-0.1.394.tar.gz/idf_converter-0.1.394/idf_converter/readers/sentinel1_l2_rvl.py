# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-07
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
import copy
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


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
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
    return ('\n'.join(inp), '\t'.join(out))


def _get_name_and_time_range(f_handler: netCDF4.Dataset,
                             input_path: str
                             ) -> typing.Tuple[str, str, str]:
    """"""
    _granule_name = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(_granule_name)
    start_str = f_handler.firstMeasurementTime
    stop_str = f_handler.lastMeasurementTime

    # L2 NetCDF filename and first/lastMeasurementTime attributes are not
    # reliable on older versions of the IPF, so acquire the info from the name
    # of the source SAFE instead
    _ipf_version = getattr(f_handler, 'IPFversion', 0.0)
    ipf_version = float(_ipf_version)
    if ipf_version < 3.4:
        source_product = f_handler.sourceProduct
        source_split = source_product.split('_')
        start_str = source_split[6]
        start_dt = datetime.datetime.strptime(start_str, '%Y%m%dT%H%M%S')
        start_str = f'{start_dt:%Y-%m-%dT%H:%M:%SZ}'
        stop_str = source_split[7]
        stop_dt = datetime.datetime.strptime(stop_str, '%Y%m%dT%H%M%S')
        stop_str = f'{stop_dt:%Y-%m-%dT%H:%M:%SZ}'
        unique_str = source_split[-1].split('.')[0]
        granule_name = f'{granule_name}_{unique_str}'

    return granule_name, start_str, stop_str


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
    variables: typing.Dict[str, typing.Dict[str, typing.Any]]
    variables = {'rvlRadVel': {'name': 'rvlRadVel',
                               'options': {}},
                 'rvlRadVelStd': {'name': 'rvlRadVelStd',
                                  'options': {}},
                 'rvlUssX': {'name': 'rvlUssX',
                             'options': {}},
                 'rvlUssY': {'name': 'rvlUssY',
                             'options': {}},
                 'rvlSnr': {'name': 'rvlSnr',
                            'options': {}},
                 'rvlHeading': {},
                 'rvlIncidenceAngle': {},
                 'rvlSweepAngle': {}}

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    # Read variables
    f_handler = netCDF4.Dataset(input_path, 'r')
    for var_id in variables.keys():
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        _band = idf_converter.lib.extract_variable_values(f_handler, var_id)
        granule.vars[var_id]['array'] = numpy.ma.array(_band)
    lon = idf_converter.lib.extract_variable_values(f_handler, 'rvlLon')
    lat = idf_converter.lib.extract_variable_values(f_handler, 'rvlLat')
    _granule_name, start_str, stop_str = _get_name_and_time_range(f_handler,
                                                                  input_path)
    # TODO: check if we should use rvlZeroDopplerTime instead
    _platform = f_handler.missionName
    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)
    nsubswath = 0
    has_subswath = 'rvlSwath' in f_handler.dimensions
    if has_subswath:
        nsubswath = f_handler.dimensions['rvlSwath'].size
    f_handler.close()

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    if 0 >= nsubswath:
        for key in granule.vars:
            fake_subswath = granule.vars[key]['array'][:, :, numpy.newaxis]
            granule.vars[key]['array'] = fake_subswath
        nsubswath = 1

    if '.' in start_str:
        start_dt = datetime.datetime.strptime(start_str,
                                              '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%SZ')

    if '.' in stop_str:
        stop_dt = datetime.datetime.strptime(stop_str,
                                             '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        stop_dt = datetime.datetime.strptime(stop_str, '%Y-%m-%dT%H:%M:%SZ')
    platform = f'Sentinel-1{_platform[-1].upper()}'

    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = 1000  # TODO: check this
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = platform
    granule.meta['sensor'] = 'C-SAR'

    # Include the L2 SAFE name as a global attribute if the input file was in
    # a SAFE directory layout
    input_dir = os.path.dirname(input_path)
    parent_name = os.path.basename(input_dir)
    if 'measurement' == parent_name:
        grandparent_name = os.path.basename(os.path.dirname(input_dir))
        if grandparent_name.endswith('.SAFE'):
            granule.meta['L2_SAFE'] = grandparent_name

    for subswath in range(0, nsubswath):

        # Replicate information shared by all subgranules
        subgranule = idf_converter.lib.create_granule(granule.idf_version,
                                                      granule.data_model)
        subgranule.meta = copy.deepcopy(granule.meta)
        subgranule.dims = copy.deepcopy(granule.dims)

        subgranule.meta['idf_granule_id'] = f'{_granule_name}_{subswath}'

        # Make sure to keep only slices where geographical coordinates are
        # fully defined
        sublon = granule.vars['lon']['array'][:, :, subswath]
        sublat = granule.vars['lat']['array'][:, :, subswath]
        valid_mask = (~numpy.ma.getmaskarray(sublon) &
                      ~numpy.ma.getmaskarray(sublat))
        valid_ind = numpy.where(valid_mask)
        valid_slices = (slice(valid_ind[0].min(), valid_ind[0].max() + 1),
                        slice(valid_ind[1].min(), valid_ind[1].max() + 1),
                        subswath)

        # Adapt dimensions
        sub_nrow = 1 + valid_ind[0].max() - valid_ind[0].min()
        sub_ncell = 1 + valid_ind[1].max() - valid_ind[1].min()
        subgranule.dims['row'] = int(sub_nrow)
        subgranule.dims['cell'] = int(sub_ncell)

        # Adapt variables
        subvars: typing.Dict[str, typing.Dict[str, typing.Any]] = {}
        for var_id in granule.vars.keys():
            subvars[var_id] = {}
            for attr_name, attr_value in granule.vars[var_id].items():
                if 'array' == attr_name:
                    _values = attr_value[valid_slices]
                    subvars[var_id]['array'] = _values
                    subvars[var_id]['valid_min'] = numpy.nanmin(_values)
                    subvars[var_id]['valid_max'] = numpy.nanmax(_values)
                else:
                    subvars[var_id][attr_name] = attr_value
            subgranule.vars = subvars

        # Add transforms
        transforms: TransformsList = []

        transforms.append(('s1_experimental_radial_velocity',
                           {'targets': ('rvlRadVel',),
                            'outputs': ('rvlRadVelExp',),
                            'incidence_angle': 'rvlIncidenceAngle',
                            'sweep_angle': 'rvlSweepAngle'}))

        vel_vars = ('rvlRadVel', 'rvlRadVelExp')
        transforms.append(('radial_velocity_sign', {'targets': vel_vars,
                                                    'update_extrema': True,
                                                    'heading': 'rvlHeading'}))

        # Remove direction and modulus variables
        to_remove = ('rvlHeading', 'rvlSweepAngle', 'rvlIncidenceAngle')
        transforms.append(('remove_vars', {'targets': to_remove}))

        channels = ['rvlRadVel', 'rvlRadVelExp', 'rvlRadVelStd', 'rvlUssX',
                    'rvlUssY', 'rvlSnr']
        output_opts['__export'] = channels

        yield input_opts, output_opts, subgranule, transforms
