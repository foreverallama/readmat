from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytz  # type: ignore


class MatDateTime:
    # * Formatting from MATLAB formats not supported yet
    def __init__(self, obj_dict):
        self.data = obj_dict.get("data")
        self.tz = self._extract_string(obj_dict.get("tz", "UTC"))
        self.fmt = self._extract_string(obj_dict.get("fmt", "%Y-%m-%d %H:%M:%S %Z"))

    def _extract_string(self, val):
        if isinstance(val, np.ndarray) and val.size > 0:
            return val.item()
        else:
            return ""

    def get_datetime(self):
        data_array = np.atleast_1d(self.data)
        # If empty/missing value
        if data_array.size == 0:
            return None

        real_part = data_array.real.astype("int64")  # milliseconds
        imag_part = data_array.imag.astype("int64")  # microseconds

        # Convert to UTC datetimes
        dt_utc = np.vectorize(
            lambda r, i: datetime.fromtimestamp(r / 1000, tz=timezone.utc).replace(
                microsecond=i
            )
        )(real_part, imag_part)

        try:
            tz_obj = pytz.timezone(self.tz)
            dt_local = np.vectorize(lambda dt: dt.astimezone(tz_obj))(dt_utc)
        except pytz.UnknownTimeZoneError:
            dt_local = dt_utc  # Fallback to UTC if invalid timezone

        return dt_local.reshape(self.data.shape)

    def __str__(self):
        """Return formatted datetime(s) as string, preserving shape."""
        dt_array = self.get_datetime()
        if dt_array is None:
            return ""

        if isinstance(dt_array, (list, np.ndarray)):
            fmt = "%Y-%m-%d %H:%M:%S %Z"  # Custom formats not yet supported
            return str([dt.strftime(fmt) for dt in dt_array])

        return dt_array.strftime(self.fmt)

    def __repr__(self):
        return f"MatDatetime(data={self.data}, tz='{self.tz}', fmt='{self.fmt}')"

    def __getitem__(self, index):
        """Allow indexing to retrieve formatted duration values"""
        datetime = self.get_datetime()
        if datetime is None:
            return None
        if isinstance(datetime, np.ndarray):
            return datetime[index]
        else:
            return datetime


class MatDuration:
    # * Formatting from MATLAB formats not supported yet
    def __init__(self, obj_dict):
        self.millis = obj_dict.get("millis")
        self.fmt = self._extract_string(obj_dict.get("fmt", "hh:mm:ss"))

    def _extract_string(self, val):
        if isinstance(val, np.ndarray) and val.size > 0:
            return val.item()
        else:
            return ""

    def get_duration(self):
        """Calculate (s, m, h, d) based on fmt"""
        if self.millis.size == 0:  # Handle empty case
            return None

        if self.fmt == "s":
            return self.millis / 1000  # Seconds
        elif self.fmt == "m":
            return self.millis / 60000  # Minutes
        elif self.fmt == "h":
            return self.millis / 3600000  # Hours
        elif self.fmt == "d":
            return self.millis / 86400000  # Days
        elif self.fmt == "hh:mm:ss":
            return self.millis  # Keep in milliseconds, format later in __str__
        else:
            return self.millis  # Default

    def __str__(self):
        """Return a formatted string"""
        durations = self.get_duration()
        if durations is None:
            return ""

        def format_value(val):
            """Apply proper formatting for string output, with correct negative duration handling."""

            if self.fmt == "s":
                return f"{val:.3f} sec"
            elif self.fmt == "m":
                return f"{val:.3f} min"
            elif self.fmt == "h":
                return f"{val:.3f} hr"
            elif self.fmt == "d":
                return f"{val:.3f} days"
            elif self.fmt == "hh:mm:ss":
                seconds = val / 1000
                sign = "-" if seconds < 0 else ""
                seconds = abs(seconds)
                h, rem = divmod(seconds, 3600)
                m, s = divmod(rem, 60)
                return f"{sign}{int(h)}:{int(m):02d}:{int(s):02d}"
            else:
                return f"{val:.3f} ms"  # Default case

        # Apply formatting while keeping N-D shape
        formatted = np.vectorize(format_value, otypes=[str])(durations)
        return np.array2string(formatted, separator=", ")

    def __repr__(self):
        return f"MatDuration(millis={self.millis}, fmt='{self.fmt}')"

    def __getitem__(self, index):
        """Allow indexing to retrieve formatted duration values"""
        durations = self.get_duration()
        if durations is None:
            return None

        if isinstance(durations, np.ndarray):
            return durations[index]  # Preserve shape and index properly
        else:
            return durations  # If single value, return directly


def parse_string(data, byte_order):
    # Skip data[0], not sure what it flags
    ndims = data[0, 1]
    shape = data[0, 2 : 2 + ndims]
    num_strings = np.prod(shape)
    char_counts = data[0, 2 + ndims : 2 + ndims + num_strings]
    offset = 2 + ndims + num_strings  # start of string data
    byte_data = data[0, offset:].tobytes()

    strings = []
    pos = 0
    encoding = "utf-16-le" if byte_order == "<" else "utf-16-be"
    for char_count in char_counts:
        byte_length = char_count * 2  # UTF-16 encoding
        extracted_string = byte_data[pos : pos + byte_length].decode(encoding)
        strings.append(extracted_string)
        pos += byte_length

    data = np.reshape(strings, shape, order="F")

    return data


class MatTable:
    def __init__(self, obj_dict):
        self.data = obj_dict.get("data")
        self.ndims = obj_dict.get("ndims")
        self.nrows = obj_dict.get("nrows")
        self.nvars = obj_dict.get("nvars")
        self.rownames = obj_dict.get("rownames")
        self.varnames = obj_dict.get("varnames")
        self.props = obj_dict.get("props")
        self._df = None

    def __repr__(self):
        return repr(self._df)

    def __str__(self):
        return str(self._df)

    def _extract_cell_value(self, cell):
        if isinstance(cell, np.ndarray) and cell.dtype == object:
            return cell[0, 0]["__fields__"]
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

    @property
    def df(self):
        if self._df is None:
            self._df = self._build_dataframe()
        return self._df

    def __getitem__(self, key):
        return self.df[key]


class MatTimetable:
    def __init__(self, obj_dict):
        self.any = obj_dict.get("any")[0, 0]
        self.data = self.any["data"]
        self.numDims = self.any["numDims"]
        self.dimNames = self.any["dimNames"]
        self.varNames = self.any["varNames"]
        self.numRows = self.any["numRows"]
        self.numVars = self.any["numVars"]
        self.rowTimes = self.any["rowTimes"]
        self._df = None

    def __str__(self):
        return str(self._df)

    def __repr__(self):
        return repr(self._df)

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

    @property
    def df(self):
        if self._df is None:
            self._df = self._build_dataframe()
        return self._df

    def __getitem__(self, key):
        return self.df[key]


def convert_to_object(fields, class_name, byte_order):
    """Converts the object to a Python compatible object"""

    if class_name == "datetime":
        obj = MatDateTime(fields)

    elif class_name == "duration":
        obj = MatDuration(fields)

    elif class_name == "string":
        if "any" in fields:
            obj = parse_string(
                fields["any"],
                byte_order=byte_order,
            )

    elif class_name == "table":
        obj = MatTable(fields)

    elif class_name == "timetable":
        if "any" in fields:
            obj = MatTimetable(fields)

    else:
        # For all other classes, return raw data
        obj = fields

    return obj
