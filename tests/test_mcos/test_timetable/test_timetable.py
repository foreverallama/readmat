import os

import numpy as np
import pandas as pd
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_df, file_name, var_name",
    [
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
            "tt1.mat",
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
            "tt2.mat",
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
            "tt3.mat",
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
            "tt4.mat",
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
            "tt5.mat",
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
            "tt6.mat",
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
            "tt7.mat",
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
            "tt8.mat",
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
            "tt10.mat",
            "tt10",
        ),
    ],
    ids=[
        "simple-timetable-datetime",
        "simple-timetable-datetime-multicolumn",
        "simple-timetable-datetime-multivars",
        "timetable-samplerate",
        "timetable-timestep",
        "timetable-samplerate-starttime",
        "timetable-timestep-starttime",
        "timetable-varnames",
        "timetable-calendarDuration-timestep",
    ],
)
def test_parse_timetable(expected_df, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)


@pytest.mark.parametrize(
    "expected_df, file_name, var_name",
    [
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
            "tt9.mat",
            "tt9",
        ),
    ],
    ids=["timetable-with-attrs"],
)
def test_parse_table_with_attrs(expected_df, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
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
