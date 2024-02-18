# vim: ts=4:sts=4:sw=4
#
# @date 2020-09-30
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


TIMEFMT = '%Y-%m-%dT%H:%M:%S.%fZ'

SUPPORTED_MODELS = {
    'grid_latlon': ('time', 'lat', 'lon', True, True),
    'grid_yx': ('time', 'y', 'x', False, True),
    'swath': ('time', 'row', 'cell', False, False),
    'time_dependent': ('time', False, False)}

MANDATORY_ATTRIBUTES = (
    'idf_version',
    'idf_granule_id',
    'idf_subsampling_factor',
    'idf_spatial_resolution',
    'idf_spatial_resolution_units',
    'time_coverage_start',
    'time_coverage_end')

SUPPORTED_ATTRIBUTES = (
    'title',
    'institution',
    'comment',
    'id',
    'product_version',
    'geospatial_lat_max',
    'geospatial_lat_min',
    'geospatial_lon_max',
    'geospatial_lon_min',
    'creator_email')

CF_ATTRIBUTES = (
    'Conventions',
    'summary',
    'references',
    'institution_abbreviation',
    'history',
    'naming_authority',
    'processing_software',
    'uuid',
    'date_created',
    'date_modified',
    'keywords',
    'keywords_vocabulary',
    'publisher_name',
    'publisher_url')

OPTIONAL_ATTRIBUTES = (
    'license',
    'netcdf_version_id',
    'file_quality_level',
    'spatial_resolution',
    'time_coverage_resolution',
    'geospatial_vertical_min',
    'geospatial_vertical_max',
    'geospatial_vertical_units',
    'geospatial_vertical_positive',
    'nominal_latitude',
    'nominal_longitude',
    'source',
    'source_version',
    'wmo_id',
    'buoy_network',
    'station_name',
    'sea_floor_depth_below_sea_level',
    'site_elevation',
    'platform_type',
    'band',
    'sensor_description',
    'sensor_manufacturer',
    'sensor_serial_number',
    'sensor_install_date',
    'sensor_height',
    'sensor_sampling_period',
    'sensor_sampling_rate',
    'sensor_calibration_date',
    'sensor_history',
    'sensor_type',
    'Metadata_Conventions',
    'metadata_link',
    'standard_name_vocabulary',
    'acknowledgement',
    'creator_name',
    'creator_url',
    'publisher_email',
    'processing_level',
    'cdm_data_type')

SPECIAL_ATTRIBUTES = (
    'platform',
    'sensor',
    'station_id',
    'forecast_range',
    'run_time',
    'forecast_type',
    'field_type')

SENSOR_CODES = (
    'altimeter',
    'sar',
    'infrared radiometer',
    'microwave radiometer')

PLATFORM_CODES = (
    'leo satellite',
    'geostationary satellite',
    'moored buoy',
    'drifting buoy',
    'ship',
    'argo')

VARIABLE_MANDATORY_ATTRIBUTES = (
    'name',
    '_FillValue',
    'scale_factor',
    'add_offset')

VARIABLE_CF_ATTRIBUTES = (
    'units',
    'long_name',
    'valid_min',
    'valid_max',
    'standard_name')

VARIABLE_OPTIONAL_ATTRIBUTES = (
    'comment',
    'axis',
    'positive',
    'coordinates',
    'flag_meanings',
    'flag_values',
    'flag_masks',
    'depth',
    'height')

NUMERICAL_ATTRIBUTES = (
    'idf_subsampling_factor',
    'idf_spatial_resolution',
    'geospatial_lat_max',
    'geospatial_lat_min',
    'geospatial_lon_max',
    'geospatial_lon_min',
    'file_quality_level',
    'sea_floor_depth_below_sea_level',
    'site_elevation',
    'geospatial_vertical_min',
    'geospatial_vertical_max',
    'nominal_latitude',
    'nominal_longitude')

TEXT_ATTRIBUTES = (
    'idf_version',
    'idf_granule_id',
    'idf_spatial_resolution_units',
    'time_coverage_start',
    'time_coverage_end',
    'title',
    'institution',
    'comment',
    'id',
    'product_version',
    'creator_email',
    'Conventions',
    'summary',
    'references',
    'institution_abbreviation',
    'history',
    'naming_authority',
    'processing_software',
    'uuid',
    'date_created',
    'date_modified',
    'keywords',
    'keywords_vocabulary',
    'publisher_name',
    'publisher_url',
    'license',
    'netcdf_version_id',
    'spatial_resolution',
    'time_coverage_resolution',
    'geospatial_vertical_units',
    'geospatial_vertical_positive',
    'source',
    'source_version',
    'wmo_id',
    'buoy_network',
    'station_name',
    'platform_type',
    'band',
    'sensor_description',
    'sensor_manufacturer',
    'sensor_serial_number',
    'sensor_install_date',
    'sensor_height',
    'sensor_sampling_period',
    'sensor_sampling_rate',
    'sensor_calibration_date',
    'sensor_history',
    'sensor_type',
    'Metadata_Conventions',
    'metadata_link',
    'standard_name_vocabulary',
    'acknowledgement',
    'creator_name',
    'creator_url',
    'publisher_email',
    'processing_level',
    'cdm_data_type',
    'platform',
    'sensor',
    'station_id',
    'forecast_range',
    'run_time',
    'forecast_type',
    'field_type')

VARIABLE_NUMERICAL_ATTRIBUTES = (
    'valid_min',
    'valid_max')

VARIABLE_TEXT_ATTRIBUTES = (
    'name',
    'units',
    'long_name',
    'standard_name',
    'comment',
    'axis',
    'positive',
    'coordinates',
    'flag_meanings',
    'depth',
    'height')
