import numpy as np
import pandas as pd


def get_col_data(coldata):
    if isinstance(coldata, np.ndarray):
        # Unravel numpy arrays
        return coldata.ravel()
    return coldata


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
        s.item() if s.size > 0 else "" for s in tab_props["VariableContinuity"].ravel()
    ]
    df.attrs["DimensionNames"] = [
        s.item() if s.size > 0 else "" for s in tab_props["DimensionNames"].ravel()
    ]
    df.attrs["UserData"] = tab_props["UserData"]

    return df


def toDataFrame(props, add_table_attrs=True):
    data = props[0, 0]["data"]
    nrows = int(props[0, 0]["nrows"].item())
    nvars = int(props[0, 0]["nvars"].item())
    varnames = props[0, 0]["varnames"]
    rownames = props[0, 0]["rownames"]
    rows = {}
    for i in range(nvars):
        coldata = data[0, i]
        coldata = get_col_data(coldata)
        rows[varnames[0, i].item()] = coldata

    df = pd.DataFrame(rows)
    if rownames.size > 0:
        rownames = [s.item() for s in rownames.ravel()]
        if len(rownames) == nrows:
            df.index = rownames

    tab_props = props[0, 0]["props"][0, 0]
    if add_table_attrs:
        # Since pandas lists this as experimental, flag so we can switch off if it breaks
        df = add_mat_props(df, tab_props)

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
