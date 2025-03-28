import numpy as np
import datetime
from datetime import datetime, timezone
import pytz

# TODO:Add support for detecting object references
# TODO:


class MatDateTime:
    # TODO: Add support for display formatting
    def __init__(self, obj_dict):

        self.data = obj_dict.get("data")
        self.tz = self._extract_string(obj_dict.get("tz", "UTC"))
        self.fmt = self._extract_string(obj_dict.get("fmt", "%Y-%m-%d %H:%M:%S %Z"))

    def _extract_string(self, val):
        return val.item() if isinstance(val, np.ndarray) and val.size > 0 else val

    def get_datetime(self):

        data_array = np.atleast_1d(self.data)
        # If empty/missing value
        if data_array.size == 0:
            return None

        real_part = data_array[0].real.astype("int64")  # milliseconds
        imag_part = data_array[0].imag.astype("int64")  # microseconds

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

        return dt_local

    def __str__(self):
        """Return formatted datetime(s) as string, preserving shape."""
        # ? Formatting from MATLAB formats not supported yet
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
            return datetime[index]  # Preserve shape and index properly
        else:
            return datetime  # If single value, return directly


class MatDuration:
    # TODO: Add support for display formatting
    def __init__(self, obj_dict):
        self.millis = obj_dict.get("millis")
        self.fmt = self._extract_string(obj_dict.get("fmt", "hh:mm:ss"))

    def _extract_string(self, val):
        return val.item() if isinstance(val, np.ndarray) and val.size > 0 else val

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
            print("Format not supported yet")
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


def parse_string(object, field_name, byte_order):

    # Skip data[0], not sure what it flags
    if field_name != "any":
        print("Field not supported yet")
        return data
    else:
        data = object["any"]

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
