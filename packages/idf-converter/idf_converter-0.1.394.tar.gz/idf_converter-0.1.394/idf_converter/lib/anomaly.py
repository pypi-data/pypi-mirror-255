# vim: ts=4:sts=4:sw=4
#
# @date 2021-03-15
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


""""""

import os
import numpy
import numpy.typing
import typing
import logging
import netCDF4
import scipy.ndimage
from scipy.interpolate import RegularGridInterpolator, griddata
from idf_converter.lib.types import InputOptions, OutputOptions, Granule
from idf_converter.lib.types import FormatterResult

logger = logging.getLogger(__name__)


def gaussian_filter_nan(array: numpy.typing.NDArray
                        ) -> numpy.typing.NDArray:
    """"""
    # Standard deviation for Gaussian kernel
    sigma = 8
    # Truncate filter at this many sigma
    truncate = sigma * 4
    # Set array with nan values to 0
    A0 = array.copy()
    array_invalid_ind = numpy.where(~numpy.isfinite(array))
    A0[array_invalid_ind] = 0
    A0g = scipy.ndimage.gaussian_filter(A0, sigma=sigma, truncate=truncate)
    # Build array with valid value set to 1, missing value to 0
    A1 = numpy.ones(A0.shape)
    A1[array_invalid_ind] = 0
    A1g = scipy.ndimage.gaussian_filter(A1, sigma=sigma, truncate=truncate)
    # Return ponderation of A0 by A1
    res: numpy.typing.NDArray = A0g / A1g
    res_invalid_mask = (~numpy.isfinite(res) | (res == 0))
    res_invalid_ind = numpy.where(res_invalid_mask)
    res[res_invalid_ind] = numpy.nan
    return res


def anomaly_from_clim(input_opts: InputOptions,
                      output_opts: OutputOptions,
                      granule: Granule,
                      *args: typing.Iterable[typing.Any],
                      climatology_path: str,
                      climatology_variable: str,
                      default_min: float,
                      default_max: float,
                      targets: typing.Tuple[str],
                      outputs: typing.Tuple[str],
                      extrapolate: bool,
                      interpolate: bool
                      ) -> FormatterResult:
    """"""
    start = granule.meta['time_coverage_start']
    stop = granule.meta['time_coverage_end']
    mid_date = start + (stop - start) / 2
    dday = mid_date.timetuple().tm_yday

    # Handle leap years case: offset everything by one day after 28th February
    if (0 == mid_date.timetuple().tm_year % 4) and (59 < dday):
        dday = dday - 1

    clim_file = climatology_path.replace('*', f'{dday:03d}')

    lon = granule.vars['lon']['array']
    lat = granule.vars['lat']['array']

    if not os.path.exists(clim_file):
        logger.warning('Anomaly not computed due to lack of climatology file')
        interp_clim_values = numpy.ma.masked_all(lon.shape)
    elif interpolate is False:
        if extrapolate is True:
            logger.warning('"extrapolate" option is ignored when the '
                           'climatology files are already on the same grid as '
                           'the input data, i.e. when the "interpolate" option'
                           ' is set to False')

        handler = netCDF4.Dataset(clim_file, 'r')
        interp_clim_values = handler[climatology_variable][0, :, :]
        handler.close()
    else:
        handler = netCDF4.Dataset(clim_file, 'r')
        clon = handler['lon'][:]
        clat = handler['lat'][:]
        cvalues = handler[climatology_variable][0, :, :]
        handler.close()
        clon2d, clat2d = numpy.meshgrid(clon, clat)

        if extrapolate is True:
            marray = numpy.ma.masked_invalid(cvalues)
            valid_ind = numpy.where(~numpy.ma.getmaskarray(marray))
            mlon = clon2d[valid_ind]
            mlat = clat2d[valid_ind]
            mcvalues = cvalues[valid_ind]
            cvalues = griddata((mlat, mlon), mcvalues.ravel(),
                               (clat2d, clon2d), method='nearest')

        func_interp = RegularGridInterpolator((clat, clon), cvalues,
                                              bounds_error=False,
                                              fill_value=None)
        if len(numpy.shape(lon)) == 1:
            lon, lat = numpy.meshgrid(granule.vars['lon']['array'],
                                      granule.vars['lat']['array'])

        interp_clim_values_1d = func_interp((lat.ravel(), lon.ravel()),
                                            method='linear')
        interp_clim_values = interp_clim_values_1d.reshape(lon.shape)

    for input_var, output_var in zip(targets, outputs):
        _input = granule.vars[input_var]['array']
        _input_mask_ind = numpy.where(numpy.isnan(_input))

        if output_var not in granule.vars.keys():
            granule.vars[output_var] = {}

        granule.vars[output_var]['name'] = output_var
        granule.vars[output_var]['options'] = {}
        granule.vars[output_var]['array'] = _input - interp_clim_values
        granule.vars[output_var]['array'][_input_mask_ind] = numpy.nan

        output_var_data = granule.vars[output_var]['array']
        output_var_mask = (numpy.ma.getmaskarray(output_var_data)
                           | ~numpy.isfinite(output_var_data))
        if 'valid_min' not in granule.vars[output_var].keys():
            vmin = default_min
            if not output_var_mask.all():
                vmin = max(default_min, numpy.nanmin(output_var_data))
            granule.vars[output_var]['valid_min'] = vmin

        if 'valid_max' not in granule.vars[output_var].keys():
            vmax = default_max
            if not output_var_mask.all():
                vmax = min(default_max, numpy.nanmax(output_var_data))
            granule.vars[output_var]['valid_max'] = vmax
    return (input_opts, output_opts, granule)
