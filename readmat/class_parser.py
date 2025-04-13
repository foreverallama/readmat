import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytz

# TODO: Add support for following classes:
# 1. dynamicprops
# 2. function_handle
# 3. event.proplistener


def MatDatetime(props):
    """Initialize the MatDatetime object"""

    if "data" in props.dtype.names:
        data = props["data"]
    else:
        data = np.array([])
    if "fmt" in props.dtype.names:
        fmt = props["fmt"]
    else:
        fmt = np.array("%Y-%m-%d %H:%M:%S %Z")
    if "tz" in props.dtype.names:
        tz = props["tz"]
    else:
        tz = np.array("UTC")
    # Not considering default values for fmt, tz as they are empty

    if data.size == 0:
        return np.array([])

    real_part = data.real.astype("int64")  # milliseconds
    imag_part = data.imag.astype("int64")  # microseconds

    # Convert to UTC datetimes
    dt_utc = np.vectorize(
        lambda r, i: datetime.fromtimestamp(r / 1000, tz=timezone.utc).replace(
            microsecond=i
        )
    )(real_part, imag_part)

    try:
        tz_obj = pytz.timezone(tz.item())
        dt_local = np.vectorize(lambda dt: dt.astimezone(tz_obj))(dt_utc)
    except pytz.UnknownTimeZoneError:
        dt_local = dt_utc  # Fallback to UTC if invalid timezone

    # Format ignored as MATLAB formatting string is not directly supported
    return np.array(
        [(dt_local.reshape(data.shape), fmt, tz)],
        dtype=[("datetime", "O"), ("fmt", "O"), ("tz", "O")],
    )


def MatDuration(props, defaults):
    """Initialize the MatDuration object"""
    if "millis" in props.dtype.names:
        millis = props["millis"]
    else:
        millis = np.array([])
    if "fmt" in props.dtype.names:
        fmt = props["fmt"]
    else:
        fmt = defaults["fmt"].item()

    if millis.size == 0:
        return np.array([])

    if fmt == "s":
        count = millis / 1000  # Seconds
    elif fmt == "m":
        count = millis / 60000  # Minutes
    elif fmt == "h":
        count = millis / 3600000  # Hours
    elif fmt == "d":
        count = millis / 86400000  # Days
    elif fmt == "hh:mm:ss":
        count = millis  # Keep in milliseconds, format later in __str__
    else:
        count = millis  # Default

    return np.array(
        [(count.reshape(props.shape), fmt)],
        dtype=[("millis", "O"), ("fmt", "O")],
    )


def parse_string(data, byte_order, uint16_codec, chars_as_strings):
    """Parse string data from MATLAB file"""

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
    # uint16_codec is note used currently
    encoding = "utf-16-le" if byte_order[0] == "<" else "utf-16-be"
    for char_count in char_counts:
        byte_length = char_count * 2  # UTF-16 encoding
        extracted_string = byte_data[pos : pos + byte_length].decode(encoding)
        strings.append(extracted_string)
        pos += byte_length

    if chars_as_strings:
        return np.array(strings, dtype=object).reshape(shape, order="F")
    return np.reshape(strings, shape, order="F")


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


def convert_to_object(
    props, defaults, class_name, byte_order, uint16_codec, chars_as_strings
):
    """Converts the object to a Python compatible object"""
    # First unwrap props and defaults
    if class_name == "datetime":
        obj = MatDatetime(props[0, 0])

    elif class_name == "duration":
        obj = MatDuration(props[0, 0], defaults)

    elif class_name == "string":
        if "any" in props.dtype.names:
            obj = parse_string(
                props["any"][0, 0],
                byte_order=byte_order,
                uint16_codec=uint16_codec,
                chars_as_strings=chars_as_strings,
            )

    elif class_name == "table":
        obj = MatTable(props[0, 0], defaults)

    elif class_name == "timetable":
        if "any" in props.dtype.names:
            obj = MatTimetable(props[0, 0], defaults)

    else:
        # For all other classes, return raw data
        obj = props

    return obj
