# vim: ts=4:sts=4:sw=4
#
# @date 2019-10-21
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

"""This module contains methods for parsing and transforming time-related
attributes."""

import numpy
import numpy.typing
import typing
import logging
import datetime
import dateutil.relativedelta
from idf_converter.lib.types import InputOptions, CoverageInfo, Coverage
from idf_converter.lib.types import Duration, Granule

logger = logging.getLogger(__name__)
AnyDatetime = typing.Union[datetime.datetime, numpy.ndarray,
                           typing.List[datetime.datetime]]


class MissingTimeCoverageRelativeBounds(ValueError):
    """Error raised when either the "time_coverage_relative_start" or the
    "time_coverage_relative_end" input options have not been specified whereas
    they are required to build sub-granule in case the input file contains
    several times."""
    pass


class InvalidDatetimeFormat(ValueError):
    """Error raised when a datetime passed as a string cannot be parsed due to
    its format."""
    def __init__(self, value: str) -> None:
        """"""
        self.invalid_string = value


class WrongTimeOffsetType(TypeError):
    """Error raised when a relative time coverage bound is neither a string nor
    a float."""
    def __init__(self, value: typing.Any) -> None:
        self.value = value


def parse_datetime(value: str, fmt: typing.Optional[str] = None
                   ) -> datetime.datetime:
    """"""
    if fmt is not None:
        try:
            dt_value = datetime.datetime.strptime(value, fmt)
            return dt_value
        except ValueError:
            raise InvalidDatetimeFormat(value)

    # Fix quirks with number of hours
    if '59:59:59' in value:
        value = value.replace('59:59:59', '23:59:59')
    if '595959' in value:
        value = value.replace('595959', '235959')

    # Fix datetimes provided with millisecond precision
    if '.' == value[-5]:
        value = value.replace('Z', '000Z')
    elif '.' == value[-4]:
        value = f'{value}000'

    # Fix UTC datetimes that include spaces before the "Z" timezone
    while value.endswith(' Z'):
        value = value.replace(' Z', 'Z')

    time_fmts = ('%Y-%m-%dT%H:%M:%S.%fZ',
                 '%Y-%m-%dT%H:%M:%SZ',
                 '%Y-%m-%dT%H:%M:%S',
                 '%Y%m%dT%H%M%S.%fZ',
                 '%Y%m%dT%H%M%SZ',
                 '%Y%m%dT%H%M%S',
                 '%Y%m%d %H%M%S.%fZ',
                 '%Y%m%d %H%M%SZ',
                 '%Y%m%d %H%M%S',
                 '%Y-%m-%d %H:%M:%S.%fZ',
                 '%Y-%m-%d %H:%M:%SZ',
                 '%Y-%m-%d %H:%M:%S',
                 '%Y%m%d%H%M%S.%fZ',
                 '%Y%m%d%H%M%SZ',
                 '%Y%m%d%H%M%S',
                 '%Y-%m-%d',
                 '%Y%m%d',
                 '%Y-%j',
                 )

    for dt_fmt in time_fmts:
        try:
            dt_value = datetime.datetime.strptime(value, dt_fmt)
            break
        except ValueError:
            pass  # silenced
    else:
        raise InvalidDatetimeFormat(value)
    return dt_value


def get_duration_from_iso8601(iso8601_str: str) -> typing.Optional[Duration]:
    """"""
    if not iso8601_str.startswith('P'):
        return None

    time_index = iso8601_str.find('T')
    year_index = iso8601_str.find('Y')
    month_index = iso8601_str[:time_index].find('M')
    day_index = iso8601_str.find('D')
    hour_index = iso8601_str.find('H', time_index)
    minute_index = iso8601_str.find('M', time_index)
    second_index = iso8601_str.find('S', time_index)

    latest_index = 0 + 1

    years = 0
    if -1 < year_index:
        years = int(iso8601_str[latest_index:year_index])
        latest_index = year_index + 1

    months = 0
    if -1 < month_index:
        months = int(iso8601_str[latest_index:month_index])
        latest_index = year_index + 1

    days = 0
    if -1 < day_index:
        days = int(iso8601_str[latest_index:day_index])
        latest_index = year_index + 1

    latest_index = time_index + 1

    hours = 0
    if -1 < hour_index:
        hours = int(iso8601_str[latest_index:hour_index])
        latest_index = year_index + 1

    minutes = 0
    if -1 < minute_index:
        minutes = int(iso8601_str[latest_index:minute_index])
        latest_index = year_index + 1

    seconds = 0
    if -1 < second_index:
        seconds = int(iso8601_str[latest_index:second_index])

    result = dateutil.relativedelta.relativedelta(years=years, months=months,
                                                  days=days, hours=hours,
                                                  minutes=minutes,
                                                  seconds=seconds)
    return result


def _get_time_coverage_info(input_opts: InputOptions,
                            granule: Granule) -> CoverageInfo:
    """"""
    start = granule.meta.get('time_coverage_start', None)
    end = granule.meta.get('time_coverage_end', None)

    # Relative offset for time coverage lower bound
    relative_start = input_opts.get('time_coverage_relative_start', None)
    if relative_start is not None:
        if isinstance(relative_start, str):
            if 'month_beginning' == relative_start.lower():
                relative_start = 'month_beginning'
            elif 'month_end' == relative_start.lower():
                relative_start = 'month_end'
            else:
                relative_start = float(relative_start)
        else:
            relative_start = None

    # Relative offset for time coverage upper bound
    relative_end = input_opts.get('time_coverage_relative_end', None)
    if relative_end is not None:
        if isinstance(relative_end, str):
            if 'month_beginning' == relative_end.lower():
                relative_end = 'month_beginning'
            elif 'month_end' == relative_end.lower():
                relative_end = 'month_end'
            else:
                relative_end = float(relative_end)
        else:
            relative_end = None

    return (start, end, relative_start, relative_end)


def get_time_coverages(input_opts: InputOptions,
                       granule: Granule,
                       dtimes: numpy.typing.NDArray,
                       ) -> typing.List[Coverage]:
    """"""

    coverage_info = _get_time_coverage_info(input_opts, granule)
    start, end, relative_start, relative_end = coverage_info
    has_offsets = (None not in (relative_start, relative_end))

    if 1 >= len(dtimes):
        if (start is not None) and (end is not None) and not has_offsets:
            # Boundaries are already defined and relative bounds (higher
            # priority)  have not been specified so there is nothing else to do
            return [(start, end), ]

    # From this point on, relative bounds are mandatory
    if has_offsets is False:
        logger.error('time_coverage_relative_start and '
                     'time_coverage_relative_end must be provided in '
                     'order to extract granules at several times from '
                     'a single input file, or if ')
        raise MissingTimeCoverageRelativeBounds()

    bounds: typing.List[Coverage] = []
    for i in range(0, dtimes.size):
        # Might happen with forecast data that allocate enough entries for
        # their final form but or not complete yet. For example a forecast
        # at hourly time resolution, distributed as one file per day: the
        # size of the time dimension can be 24 even if all time slots are
        # not filled at first because the model will fill them eventually,
        # in future runs.
        if (dtimes[i] is None) or (dtimes[i] is numpy.ma.masked):
            logger.warning(f'{i+1}th time is invalid and has been skipped')
            bounds.append((None, None))
            continue

        if 'month_beginning' == relative_start:
            start_dt = datetime.datetime(dtimes[i].year, dtimes[i].month, 1)
        elif 'month_end' == relative_start:
            one_month = dateutil.relativedelta.relativedelta(months=1)
            one_microsecond = datetime.timedelta(microseconds=1)
            _start_dt = datetime.datetime(dtimes[i].year, dtimes[i].month, 1)
            start_dt = _start_dt + one_month - one_microsecond
        else:
            time_offset = None
            if isinstance(relative_start, str):
                time_offset = float(relative_start)
            elif isinstance(relative_start, float):
                time_offset = relative_start
            else:
                raise WrongTimeOffsetType(relative_start)
            start_dt = dtimes[i] + datetime.timedelta(seconds=time_offset)

        if 'month_beginning' == relative_end:
            stop_dt = datetime.datetime(dtimes[i].year, dtimes[i].month, 1)
        elif 'month_end' == relative_end:
            one_month = dateutil.relativedelta.relativedelta(months=1)
            one_microsecond = datetime.timedelta(microseconds=1)
            _stop_dt = datetime.datetime(dtimes[i].year, dtimes[i].month, 1)
            stop_dt = _stop_dt + one_month - one_microsecond
        else:
            time_offset = None
            if isinstance(relative_end, str):
                time_offset = float(relative_end)
            elif isinstance(relative_end, float):
                time_offset = relative_end
            else:
                raise WrongTimeOffsetType(relative_end)
            stop_dt = dtimes[i] + datetime.timedelta(seconds=time_offset)

        bounds.append((start_dt, stop_dt,))
    return bounds


def as_datetimes_array(dtimes: AnyDatetime
                       ) -> numpy.typing.NDArray:
    """"""
    dt_cast = '_to_real_datetime'
    if hasattr(dtimes, dt_cast):
        # conversion from cftime + scalar -> 1-item array
        return numpy.array([getattr(dtimes, dt_cast)()])
    elif isinstance(dtimes, datetime.datetime):
        # scalar -> 1-item array
        return numpy.array([dtimes])

    return numpy.array([getattr(_, dt_cast)()
                        if ((_ is not None) and hasattr(_, dt_cast))
                        else _
                        for _ in dtimes])
