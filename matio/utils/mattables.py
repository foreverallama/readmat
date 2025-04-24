import numpy as np
import pandas as pd


def add_table_props(df, tab_props):
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


def add_timetable_props(df, tab_props):
    """Add MATLAB table properties to pandas DataFrame
    These properties are mostly cell arrays of character vectors
    """
    df.attrs["varDescriptions"] = [
        s.item() if s.size > 0 else "" for s in tab_props["varDescriptions"].ravel()
    ]
    df.attrs["varUnits"] = [
        s.item() if s.size > 0 else "" for s in tab_props["varUnits"].ravel()
    ]
    df.attrs["varContinuity"] = [
        s.item() if s.size > 0 else "" for s in tab_props["varContinuity"].ravel()
    ]
    df.attrs["UserData"] = tab_props["arrayProps"]["UserData"][0, 0]
    df.attrs["Description"] = (
        tab_props["arrayProps"]["Description"][0, 0].item()
        if tab_props["arrayProps"]["Description"][0, 0].size > 0
        else ""
    )

    return df


def toDataFrame(data, nvars, varnames):
    """Creates a dataframe from coldata and column names"""
    rows = {}
    for i in range(nvars):
        vname = varnames[0, i].item()
        coldata = data[0, i]

        # If variable is multicolumn data
        if isinstance(coldata, np.ndarray):
            if coldata.shape[1] == 1:
                rows[vname] = coldata[:, 0]
            else:
                for j in range(coldata.shape[1]):
                    colname = f"{vname}_{j + 1}"
                    rows[colname] = coldata[:, j]
        else:
            rows[vname] = coldata

    df = pd.DataFrame(rows)
    return df


def mat_to_table(props, add_table_attrs=False):
    """Converts MATLAB table to pandas DataFrame"""
    data = props[0, 0]["data"]
    nvars = int(props[0, 0]["nvars"].item())
    varnames = props[0, 0]["varnames"]
    df = toDataFrame(data, nvars, varnames)

    # Add df.index
    nrows = int(props[0, 0]["nrows"].item())
    rownames = props[0, 0]["rownames"]
    if rownames.size > 0:
        rownames = [s.item() for s in rownames.ravel()]
        if len(rownames) == nrows:
            df.index = rownames

    tab_props = props[0, 0]["props"][0, 0]
    if add_table_attrs:
        # Since pandas lists this as experimental, flag so we can switch off if it breaks
        df = add_table_props(df, tab_props)

    return df


def get_row_times(rowTimes, numRows):
    """Get row times from MATLAB timetable
    rowTimes is a duration or datetime array if explicitly specified
    If using "SampleRate" or "TimeStep", it is a struct array with the following fields:
    1. origin - the start time as a duration or datetime scalar
    2. specifiedAsRate - boolean indicating which to use - sampleRate or TimeStep
    3. stepSize - the time step as a duration scalar
    4. sampleRate - the sample rate as a float
    """
    if not rowTimes.dtype.names:
        return rowTimes.ravel()

    start = rowTimes[0, 0]["origin"]
    if rowTimes[0, 0]["specifiedAsRate"]:
        fs = rowTimes[0, 0]["sampleRate"].item()
        step = np.timedelta64(int(1e9 / fs), "ns")
    else:
        step = rowTimes[0, 0]["stepSize"].astype("timedelta64[ns]")

    return (start + step * np.arange(numRows)).ravel()


def mat_to_timetable(props, add_table_attrs=False):
    """Converts MATLAB timetable to pandas DataFrame"""
    numVars = int(props[0, 0]["any"][0, 0]["numVars"].item())
    varNames = props[0, 0]["any"][0, 0]["varNames"]
    data = props[0, 0]["any"][0, 0]["data"]
    df = toDataFrame(data, numVars, varNames)

    rowTimes = props[0, 0]["any"][0, 0]["rowTimes"]
    numRows = int(props[0, 0]["any"][0, 0]["numRows"].item())

    rowTimes = get_row_times(rowTimes, numRows)
    dimNames = props[0, 0]["any"][0, 0]["dimNames"]
    df.index = pd.Index(rowTimes, name=dimNames[0, 0].item())

    if add_table_attrs:
        # Since pandas lists this as experimental, flag so we can switch off if it breaks
        df = add_timetable_props(df, props[0, 0]["any"][0, 0])

    return df


def mat_to_categorical(props):
    """Converts MATLAB categorical to pandas Categorical
    MATLAB categorical objects are stored with the following properties:
    1. categoryNames - all unique categories
    2. codes
    3. isOrdinal - boolean indicating if the categorical is ordered
    4. isProtected - boolean indicating if the categorical is protected
    """

    raw_names = props[0, 0]["categoryNames"]
    category_names = [name.item() for name in raw_names.ravel()]

    # MATLAB codes are 1-indexed as uint integers
    codes = props[0, 0]["codes"].astype(int) - 1
    ordered = bool(props[0, 0]["isOrdinal"].item())
    return pd.Categorical.from_codes(codes, categories=category_names, ordered=ordered)
