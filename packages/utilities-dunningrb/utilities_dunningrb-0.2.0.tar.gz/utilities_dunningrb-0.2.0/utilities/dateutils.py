"""Define utility methods for working with dates and datetime objects.
"""
from __future__ import annotations

import calendar
from datetime import datetime, timedelta

SHORT_DATE_FORMAT = "%Y-%m-%d"  # ISO-8601.


def check_date_format(*, date: str, dtformat: str = None) -> bool:
    """Return True if the given <<date>> is formatted according to
    <<dt_format>>, otherwise False.
    """
    dtformat = SHORT_DATE_FORMAT if dtformat is None else dtformat
    try:
        datetime.strptime(date, dtformat)
    except ValueError:
        return False
    return True


def get_date_ahead(r: datetime = datetime.now(), *, days_ahead: int) -> datetime:
    return r + timedelta(days_ahead)


def get_date_short_str(*, date: datetime) -> str:
    return date.strftime(SHORT_DATE_FORMAT)


def get_datestamp(date: datetime = None) -> str:
    now = datetime.now() if date is None else date
    return f"{now.isoformat().split('T')[0]}"


def get_datetime_instance(*, date: str) -> datetime:
    """Return a datetime instance."""
    return datetime.strptime(date, SHORT_DATE_FORMAT)


def get_julian_day(*, date: datetime) -> float:
    """Convert the given date into the Julian day number.
    """
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second

    part_a = 367 * year

    part_b_numerator = 7 * (year + int((month + 9)/12))
    part_b = int(part_b_numerator / 4)

    part_c = int((275 * month) / 9)

    universal_time = hour + minute / 60 + second / 3600
    ut_fraction = universal_time / 24

    julian_day = part_a - part_b + part_c + day + 1_721_013.5 + ut_fraction

    return julian_day


def get_last_date_of(r: datetime, *, step: str) -> datetime:
    """If step is one week, return the date for the first Sunday on or after the given date <r>.
    If step is one month, return the date for the last day of the month containing <r>.
    """
    if step.strip().lower() == "week":
        days_left = 7 - r.isoweekday()
        last_date = r + timedelta(days_left)
    elif step.strip().lower() == "month":
        last_day = calendar.monthrange(r.year, r.month)[-1]
        last_date = datetime(r.year, r.month, last_day)

    return last_date
