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

"""This module provides ."""

import numpy
import typing
import logging
import netCDF4
import pkg_resources
from idf_converter.lib.types import InputOptions, OutputOptions, ProcessedLists
from idf_converter.lib.types import Granule, FormatterResult

logger = logging.getLogger(__name__)


class IncompatibleNetCDFVersion(EnvironmentError):
    """Error raised when the version of the netCDF4 C library is too old and
    cannot create files that follow time-dependent IDF specifications."""
    def __init__(self, netcdf4_version: str) -> None:
        """"""
        self.netcdf4_version = netcdf4_version


def help() -> typing.Tuple[str, str]:
    """"""
    return ('', '')


def preformat(input_opts: InputOptions, output_opts: OutputOptions,
              granule: Granule
              ) -> typing.Iterator[FormatterResult]:
    """"""
    yield input_opts, output_opts, granule


def format_granule(input_opts: InputOptions,
                   output_opts: OutputOptions,
                   granule: Granule,
                   idf_file: netCDF4.Dataset) -> ProcessedLists:
    """Create dimensions, variables and attributes required for time-dependent
    granules.

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
    # Check that the netCDF4 C library is at least 4.7.3 as a bug prevented the
    # creation of the time-dependent variables/dimensions scheme in earlier
    # versions
    _nc_version = netCDF4.__netcdf4libversion__
    nc_version = pkg_resources.parse_version(_nc_version.split('-', 1)[0])
    ref_version = pkg_resources.parse_version('4.7.3')
    if (nc_version < ref_version) and ('4.7.3-development' != _nc_version):
        logger.error('The netCDF C library available on the system is too old '
                     'and contains a bug that prevents the converter from '
                     'creating the output IDF file. This bug has been fixed '
                     'in version 4.7.3 so make sure to update the library at '
                     'least to this version.')
        raise IncompatibleNetCDFVersion(netCDF4.__netcdf4libversion__)

    # One GCP per time
    gcplon = granule.vars['lon']['array']
    gcplat = granule.vars['lat']['array']
    times = granule.vars['time']['array']

    npix = times.shape[0]
    gcpind = numpy.arange(npix)

    # Dimensions
    idf_file.createDimension('time', None)  # unlimited
    idf_file.createDimension('time_gcp', granule.dims['time'])
    idf_dims = ('time', 'time_gcp',)
    extra_dims = [x for x in granule.dims.keys() if x not in idf_dims]
    for extra_dim in extra_dims:
        idf_file.createDimension(extra_dim, granule.dims[extra_dim])

    # Variables
    # Dimension of the "time" variable should be "time_gcp" but there is a bug
    # in netCDF4 or hdf5 wherein a variable which shares the same name as an
    # unlimited dimension must also have an limited dimension (whereas
    # "time_gcp" is a finite dimension)
    _time = idf_file.createVariable('time', 'f8', ('time_gcp',))
    _time.long_name = 'time'
    _time.standard_name = 'time'
    _time.units = 'seconds since 1970-01-01T00:00:00.000000Z'
    _time.calendar = 'standard'
    _time.axis = 'T'
    _time[:] = times

    _latgcp = idf_file.createVariable('lat_gcp', 'f4', ('time_gcp',))
    _latgcp.long_name = 'ground control points latitude'
    _latgcp.standard_name = 'latitude'
    _latgcp.units = 'degrees_north'
    _latgcp.comment = 'geographical coordinates, WGS84 projection'
    _latgcp[:] = gcplat.astype('float32')

    _longcp = idf_file.createVariable('lon_gcp', 'f4', ('time_gcp',))
    _longcp.long_name = 'ground control points longitude'
    _longcp.standard_name = 'longitude'
    _longcp.units = 'degrees_east'
    _longcp.comment = 'geographical coordinates, WGS84 projection'
    _longcp[:] = gcplon.astype('float32')

    _indexdim1gcp = idf_file.createVariable('index_time_gcp', 'i4',
                                            ('time_gcp',))
    _indexdim1gcp[:] = gcpind.astype('int32')
    _indexdim1gcp.long_name = ('index of ground control points in time '
                               'dimension')
    _indexdim1gcp.comment = ('index goes from 0 (start of first pixel) to '
                             'dimension value (end of last pixel)')

    idf_file.cdm_data_type = b'Trajectory'

    processed_dims = ['time', 'time_gcp']
    processed_vars = ['time', 'lat_gcp', 'lon_gcp', 'index_time_gcp', 'lat',
                      'lon']
    processed_attrs = ['cdm_data_type']

    return (processed_dims, processed_vars, processed_attrs)
