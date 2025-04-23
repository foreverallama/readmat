import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

# TODO: Add support for following classes:
# 1. dynamicprops
# 2. function_handle
# 3. event.proplistener


class MatTime:
    @staticmethod
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

    @staticmethod
    def toDatetime(props):
        """Convert MATLAB datetime to Python datetime
        Datetime returned as numpy.datetime64[ms]
        """

        data = props[0, 0].get("data", np.array([]))
        if data.size == 0:
            return np.array([], dtype="datetime64[ms]")
        tz = props[0, 0].get("tz", None)
        if tz.size > 0:
            offset = MatTime.get_tz_offset(tz.item())
        else:
            offset = 0

        millis = data.real + data.imag * 1e3 + offset

        return millis.astype("datetime64[ms]")

    @staticmethod
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


class MatString:
    @staticmethod
    def toString(props, byte_order):
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
            return np.array([[]], dtype=np.str_)

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
            strings.append(np.str_(extracted_string))
            pos += byte_length

        return np.reshape(strings, shape, order="F")


class MatTables:
    @staticmethod
    def get_col_data(coldata):
        if isinstance(coldata, np.ndarray):
            # Unravel numpy arrays
            return coldata.ravel()
        return coldata

    @staticmethod
    def add_mat_props(df, tab_props):
        """Add MATLAB table properties to pandas DataFrame
        These properties are mostly cell arrays of character vectors
        """

        df.attrs["Description"] = (
            tab_props["Description"].item() if tab_props["Description"].size > 0 else ""
        )
        df.attrs["VariableDescriptions"] = [
            s.item() if s.size > 0 else ""
            for s in tab_props["VariableDescriptions"].ravel()
        ]
        df.attrs["VariableUnits"] = [
            s.item() if s.size > 0 else "" for s in tab_props["VariableUnits"].ravel()
        ]
        df.attrs["VariableContinuity"] = [
            s.item() if s.size > 0 else ""
            for s in tab_props["VariableContinuity"].ravel()
        ]
        df.attrs["DimensionNames"] = [
            s.item() if s.size > 0 else "" for s in tab_props["DimensionNames"].ravel()
        ]
        df.attrs["UserData"] = tab_props["UserData"]

        return df

    @staticmethod
    def toDataFrame(props, add_table_attrs=True):
        data = props[0, 0]["data"]
        nrows = int(props[0, 0]["nrows"].item())
        nvars = int(props[0, 0]["nvars"].item())
        varnames = props[0, 0]["varnames"]
        rownames = props[0, 0]["rownames"]
        rows = {}
        for i in range(nvars):
            coldata = data[0, i]
            coldata = MatTables.get_col_data(coldata)
            rows[varnames[0, i].item()] = coldata

        df = pd.DataFrame(rows)
        if rownames.size > 0:
            rownames = [s.item() for s in rownames.ravel()]
            if len(rownames) == nrows:
                df.index = rownames

        tab_props = props[0, 0]["props"][0, 0]
        if add_table_attrs:
            # Since pandas lists this as experimental, flag so we can switch off if it breaks
            df = MatTables.add_mat_props(df, tab_props)

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


def convert_to_object(props, class_name, byte_order, raw_data=False):
    """Converts the object to a Python compatible object"""

    if raw_data:
        result = {
            "_Class": class_name,
            "_Props": props,
        }
        return result

    if class_name == "datetime":
        result = MatTime.toDatetime(props)

    elif class_name == "duration":
        result = MatTime.toDuration(props)

    elif class_name == "string":
        result = MatString.toString(props, byte_order)

    elif class_name == "table":
        result = MatTables.toDataFrame(props)

    elif class_name == "timetable":
        return props

    else:
        # For all other classes, return raw data
        result = {
            "_Class": class_name,
            "_Props": props,
        }

    return result


def wrap_enumeration_instance(enum_array, shapes):
    """Wraps enumeration instance data into a dictionary"""
    wrapped_dict = {"_Values": np.empty(shapes, dtype=object)}
    if len(enum_array) == 0:
        wrapped_dict["_Values"] = np.array([], dtype=object)
    else:
        enum_props = [item.get("_Props", np.array([]))[0, 0] for item in enum_array]
        wrapped_dict["_Values"] = np.array(enum_props).reshape(shapes, order="F")
    return wrapped_dict
