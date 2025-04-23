import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

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
    except Exception as e:
        warnings.warn(
            f"Could not get timezone offset for {tz}: {e}. Defaulting to UTC."
        )
        offset = 0
    return offset


def toDatetime(props):
    """Convert MATLAB datetime to Python datetime
    Datetime returned as numpy.datetime64[ms]
    """

    data = props[0, 0].get("data", np.array([]))
    if data.size == 0:
        return np.array([], dtype="datetime64[ms]")
    tz = props[0, 0].get("tz", None)
    if tz.size > 0:
        offset = get_tz_offset(tz.item())
    else:
        offset = 0

    millis = data.real + data.imag * 1e3 + offset

    return millis.astype("datetime64[ms]")


def toDuration(props):
    """Convert MATLAB duration to Python timedelta
    Duration returned as numpy.timedelta64
    """

    millis = props[0, 0]["millis"]
    if millis.size == 0:
        return np.array([], dtype="timedelta64[ms]")

    fmt = props[0, 0].get("fmt", None)
    if fmt == "s":
        count = millis / 1000  # Seconds
        dur = count.astype("timedelta64[s]")
    elif fmt == "m":
        count = millis / 60000  # Minutes
        dur = count.astype("timedelta64[m]")
    elif fmt == "h":
        count = millis / 3600000  # Hours
        dur = count.astype("timedelta64[h]")
    elif fmt == "d":
        count = millis / 86400000  # Days
        dur = count.astype("timedelta64[D]")
    else:
        count = millis
        dur = count.astype("timedelta64[ms]")
        # Default case

    return dur
