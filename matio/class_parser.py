import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

# TODO: Add support for following classes:
# 1. dynamicprops
# 2. function_handle
# 3. event.proplistener


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


def MatDatetime(props):
    """Convert MATLAB datetime to Python datetime
    Datetime returned as numpy.datetime64[ms]
    """

    data = props[0, 0].get("data", np.array([]))
    if data.size == 0:
        props[0, 0]["data"] = np.array([], dtype="datetime64[ms]")
        return props
    tz = props[0, 0].get("tz", None)
    if tz.size > 0:
        offset = get_tz_offset(tz.item())
    else:
        offset = 0

    millis = data.real + data.imag * 1e3 + offset

    props[0, 0]["data"] = millis.astype("datetime64[ms]")
    return props


def MatDuration(props):
    """Convert MATLAB duration to Python timedelta
    Duration returned as numpy.timedelta64
    """

    millis = props[0, 0]["millis"]
    if millis.size == 0:
        props[0, 0]["millis"] = np.array([], dtype="timedelta64[ms]")
        return props

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

    props[0, 0]["millis"] = dur
    return props


def MatString(props, byte_order):
    """Parse string data from MATLAB file
    Strings are stored within a uint64 array with the following format:
        1. version
        2. ndims
        3. shape
        4. char_counts
        5. List of null-terminated strings as uint16 integers
    """

    data = props[0, 0].get("any", np.array([]))
    if data.size == 0:
        data = np.array([[]], dtype="U")
        props[0, 0]["any"] = data
        return props

    version = data[0, 0]
    if version != 1:
        warnings.warn(
            "String saved from a different MAT-file version. This may work unexpectedly",
            UserWarning,
        )

    ndims = data[0, 1]
    shape = data[0, 2 : 2 + ndims]
    num_strings = np.prod(shape)
    char_counts = data[0, 2 + ndims : 2 + ndims + num_strings]
    offset = 2 + ndims + num_strings  # start of string data
    byte_data = data[0, offset:].tobytes()

    strings = []
    pos = 0
    encoding = "utf-16-le" if byte_order[0] == "<" else "utf-16-be"
    for char_count in char_counts:
        byte_length = char_count * 2  # UTF-16 encoding
        extracted_string = byte_data[pos : pos + byte_length].decode(encoding)
        strings.append(extracted_string)
        pos += byte_length

    arr_str = np.reshape(strings, shape, order="F")
    props[0, 0]["any"] = arr_str
    return props


class MatTable:
    # TODO: Collect cases and fix
    def __init__(self, props, defaults):
        self.data = defaults["data"]

        for field in [
            "data",
            "ndims",
            "nrows",
            "nvars",
            "rownames",
            "varnames",
            "props",
        ]:
            if field in props.dtype.names:
                setattr(self, field, props[field])

        self.df = self._build_dataframe()

    def __repr__(self):
        return repr(self.df)

    def __str__(self):
        return str(self.df)

    def _extract_cell_value(self, cell):
        if isinstance(cell, np.ndarray) and cell.dtype == object:
            return cell[0, 0]["__fields__"]
        if isinstance(cell, dict):
            return cell["__properties__"]
        return cell

    def _build_dataframe(self):
        columns = {}
        for i in range(int(self.nvars.item())):
            varname = self._extract_cell_value(self.varnames[0, i]).item()
            coldata = [
                data.item() for data in self._extract_cell_value(self.data[0, i])
            ]
            columns[varname] = coldata

        df = pd.DataFrame(columns)
        if self.rownames.size > 0:
            rownames = [self._extract_cell_value(rn) for rn in self.rownames[0]]
            if len(rownames) == self.nrows:
                df.index = rownames

        return df


class MatTimetable:
    # TODO: Collect cases and fix
    def __init__(self, obj_dict):
        self.any = obj_dict.get("any")[0, 0]
        self.data = self.any["data"]
        self.numDims = self.any["numDims"]
        self.dimNames = self.any["dimNames"]
        self.varNames = self.any["varNames"]
        self.numRows = self.any["numRows"]
        self.numVars = self.any["numVars"]
        self.rowTimes = self.any["rowTimes"]
        self.df = self._build_dataframe()

    def __str__(self):
        return str(self.df)

    def __repr__(self):
        return repr(self.df)

    def _extract_cell_value(self, cell):
        if isinstance(cell, np.ndarray) and cell.dtype == object:
            return cell[0, 0]["__fields__"]
        return cell

    def _build_dataframe(self):
        columns = {}
        for i in range(int(self.numVars.item())):
            varname = self._extract_cell_value(self.varNames[0, i]).item()
            coldata = [
                data.item() for data in self._extract_cell_value(self.data[0, i])
            ]
            columns[varname] = coldata

        df = pd.DataFrame(columns)
        time_arr = self.rowTimes[0, 0]["__fields__"]
        times = [time_arr[i].item() for i in range(int(self.numRows.item()))]
        df.index = pd.to_datetime(times)
        df.index.name = self._extract_cell_value(self.dimNames[0, 0]).item()

        return df


def convert_to_object(props, class_name, byte_order):
    """Converts the object to a Python compatible object"""

    if class_name == "datetime":
        obj = MatDatetime(props)

    elif class_name == "duration":
        obj = MatDuration(props)

    elif class_name == "string":
        obj = MatString(props, byte_order)

    # elif class_name == "table":
    #     obj = MatTable(props[0, 0], defaults)

    # elif class_name == "timetable":
    #     if "any" in props.dtype.names:
    #         obj = MatTimetable(props[0, 0], defaults)

    else:
        # For all other classes, return raw data
        obj = props

    return obj


def wrap_enumeration_instance(enum_array, shapes):
    """Wraps enumeration instance data into a dictionary"""
    wrapped_dict = {"_Values": np.empty(shapes, dtype=object)}
    if len(enum_array) == 0:
        wrapped_dict["_Values"] = np.array([], dtype=object)
    else:
        enum_props = [item.get("_Props", np.array([]))[0, 0] for item in enum_array]
        wrapped_dict["_Values"] = np.array(enum_props).reshape(shapes, order="F")
    return wrapped_dict
