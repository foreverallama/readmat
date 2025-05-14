import os

import numpy as np
import pandas as pd
import pytest

from matio import load_from_mat

params_base = [
    (
        pd.DataFrame(
            {"data1": [1.0, 2.0, 3.0]},
            index=pd.Index(
                np.array(
                    ["2023-01-01", "2023-01-02", "2023-01-03"],
                    dtype="datetime64[ms]",
                ),
                name="Time",
            ),
        ),
        "tt1",
    ),
    (
        pd.DataFrame(
            {
                "data2_1": [1.0, 2.0, 3.0],
                "data2_2": [4.0, 5.0, 6.0],
            },
            index=pd.Index(
                np.array([10, 20, 30], dtype="timedelta64[s]"),
                name="Time",
            ),
        ),
        "tt2",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
                "data3": [7.0, 8.0, 9.0],
            },
            index=pd.Index(
                np.array(
                    ["2023-01-01", "2023-01-02", "2023-01-03"],
                    dtype="datetime64[ms]",
                ),
                name="Time",
            ),
        ),
        "tt3",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
            },
            index=pd.Index(
                np.array([0, int(1e5), int(2e5)], dtype="timedelta64[ns]"),
                name="Time",
            ),
        ),
        "tt4",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
            },
            index=pd.Index(
                np.array([0, int(1e9), int(2e9)], dtype="timedelta64[ns]"),
                name="Time",
            ),
        ),
        "tt5",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
            },
            index=pd.Index(
                np.array(
                    [int(10e9), int(11e9), int(12e9)], dtype="timedelta64[ns]"
                ),
                name="Time",
            ),
        ),
        "tt6",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
            },
            index=pd.Index(
                np.array(
                    [
                        "2020-01-01T00:00:00",
                        "2020-01-01T00:00:01",
                        "2020-01-01T00:00:02",
                    ],
                    dtype="datetime64[ns]",
                ),
                name="Time",
            ),
        ),
        "tt7",
    ),
    (
        pd.DataFrame(
            {"Pressure": [1.0, 2.0, 3.0]},
            index=pd.Index(
                np.array(
                    ["2023-01-01", "2023-01-02", "2023-01-03"],
                    dtype="datetime64[ms]",
                ),
                name="Time",
            ),
        ),
        "tt8",
    ),
    (
        pd.DataFrame(
            {
                "data1": [1.0, 2.0, 3.0],
            },
            index=pd.Index(
                np.array(
                    [
                        "2020-01-01T00:00:00",
                        "2020-04-01T00:00:01",
                        "2020-07-01T00:00:02",
                    ],
                    dtype="datetime64[M]",
                ),
                name="Time",
            ),
        ),
        "tt10",
    ),
]

param_attrs = [
    (
        pd.DataFrame(
            {"data1": [1.0, 2.0, 3.0]},
            index=pd.Index(
                np.array(
                    ["2023-01-01", "2023-01-02", "2023-01-03"],
                    dtype="datetime64[ms]",
                ),
                name="Date",
            ),
        ),
        "tt9",
    ),
]

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_base,
    ids=[
        "simple-timetable-datetime-v7",
        "simple-timetable-datetime-multicolumn-v7",
        "simple-timetable-datetime-multivars-v7",
        "timetable-samplerate-v7",
        "timetable-timestep-v7",
        "timetable-samplerate-starttime-v7",
        "timetable-timestep-starttime-v7",
        "timetable-varnames-v7",
        "timetable-calendarDuration-timestep-v7",
    ],
)
def test_timetable_read_v7(expected_df, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_timetable_v7.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_base,
    ids=[
        "simple-timetable-datetime-v7.3",
        "simple-timetable-datetime-multicolumn-v7.3",
        "simple-timetable-datetime-multivars-v7.3",
        "timetable-samplerate-v7.3",
        "timetable-timestep-v7.3",
        "timetable-samplerate-starttime-v7.3",
        "timetable-timestep-starttime-v7.3",
        "timetable-varnames-v7.3",
        "timetable-calendarDuration-timestep-v7.3",
    ],
)
def test_timetable_read_v73(expected_df, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_timetable_v73.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)


@pytest.mark.parametrize(
    "expected_df, var_name",
    param_attrs,
    ids=["timetable-with-attrs-v7"],
)
def test_timetable_with_attrs_read_v7(expected_df, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_timetable_v7.mat")
    matdict = load_from_mat(file_path, raw_data=False, add_table_attrs=True)
    expected_df.attrs = {
        "Description": "Random Description",
        "varUnits": ["m/s"],
        "varDescriptions": ["myVar"],
        "varContinuity": ["continuous"],
        "UserData": np.empty((0, 0), dtype=float),
    }

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

    # Check attributes
    for key, value in expected_df.attrs.items():
        assert key in matdict[var_name].attrs
        if isinstance(value, np.ndarray):
            np.testing.assert_array_equal(matdict[var_name].attrs[key], value)
        else:
            assert matdict[var_name].attrs[key] == value

@pytest.mark.parametrize(
    "expected_df, var_name",
    param_attrs,
    ids=["timetable-with-attrs-v7.3"],
)
def test_timetable_with_attrs_read_v73(expected_df, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_timetable_v73.mat")
    matdict = load_from_mat(file_path, raw_data=False, add_table_attrs=True)
    expected_df.attrs = {
        "Description": "Random Description",
        "varUnits": ["m/s"],
        "varDescriptions": ["myVar"],
        "varContinuity": ["continuous"],
        "UserData": np.empty((0, 0), dtype=float),
    }

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

    # Check attributes
    for key, value in expected_df.attrs.items():
        assert key in matdict[var_name].attrs
        if isinstance(value, np.ndarray):
            np.testing.assert_array_equal(matdict[var_name].attrs[key], value)
        else:
            assert matdict[var_name].attrs[key] == value
