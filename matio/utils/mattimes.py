"""Utility functions for converting MATLAB datetime, duration, and calendarDuration"""

import warnings
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np


def get_tz_offset(tz):
    """Get timezone offset in milliseconds
    Inputs:
        1. tz (str): Timezone string
    Returns:
        1. offset (int): Timezone offset in milliseconds
    """
    try:
        tzinfo = ZoneInfo(tz)
        utc_offset = tzinfo.utcoffset(datetime.now())
        if utc_offset is not None:
            offset = int(utc_offset.total_seconds() * 1000)
        else:
            offset = 0
    except ZoneInfoNotFoundError as e:
        warnings.warn(
            f"Could not get timezone offset for {tz}: {e}. Defaulting to UTC."
        )
        offset = 0
    return offset


def mat_to_datetime(props):
    """Convert MATLAB datetime to Python datetime
    Datetime returned as numpy.datetime64[ms]

    MATLAB datetimes objects are stored with the following properties:
    1. data - complex number = real_part (ms) + i * imag_part (us)
    2. fmt - Format | char array
    3. tz - Timezone | char array
    """

    data = props[0, 0].get("data", np.array([]))
    if data.size == 0:
        return np.array([], dtype="datetime64[ms]")
    tz = props[0, 0].get("tz", None)
    if tz is not None and tz.size > 0:
        offset = get_tz_offset(tz.item())
    else:
        offset = 0

    millis = data.real + data.imag * 1e3 + offset

    return millis.astype("datetime64[ms]")


def mat_to_duration(props):
    """Convert MATLAB duration to Python timedelta
    Duration returned as numpy.timedelta64

    MATLAB datetimes objects are stored with the following properties:
    1. millis - double
    2. fmt - char array
    """

    millis = props[0, 0]["millis"]
    if millis.size == 0:
        return np.array([], dtype="timedelta64[ms]")

    fmt = props[0, 0].get("fmt", None)
    if fmt is None:
        return millis.astype("timedelta64[ms]")

    if fmt == "s":
        count = millis / 1000  # Seconds
        dur = count.astype("timedelta64[s]")
    elif fmt == "m":
        count = millis / (1000 * 60)  # Minutes
        dur = count.astype("timedelta64[m]")
    elif fmt == "h":
        count = millis / (1000 * 60 * 60)  # Hours
        dur = count.astype("timedelta64[h]")
    elif fmt == "d":
        count = millis / (1000 * 60 * 60 * 24)  # Days
        dur = count.astype("timedelta64[D]")
    elif fmt == "y":
        count = millis / (1000 * 60 * 60 * 24 * 365)  # Years
        dur = count.astype("timedelta64[Y]")
    else:
        count = millis
        dur = count.astype("timedelta64[ms]")
        # Default case

    return dur


def mat_to_calendarduration(props):
    """Convert MATLAB calendarDuration to Python timedelta
    CalendarDuration returned as numpy.timedelta64

    MATLAB calendarDuration objects are stored with the following properties:
    1. months - double
    2. days - double
    3. millis - double
    """

    months = props[0, 0]["components"][0, 0]["months"].astype("timedelta64[M]")
    days = props[0, 0]["components"][0, 0]["days"].astype("timedelta64[D]")
    millis = props[0, 0]["components"][0, 0]["millis"].astype("timedelta64[ms]")

    cal = np.empty((1, 1), dtype=[("calendarDuration", object)])
    cal[0, 0]["calendarDuration"] = (months, days, millis)
    return cal
