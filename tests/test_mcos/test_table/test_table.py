import os

import numpy as np
import pandas as pd
import pytest

from matio import load_from_mat


def make_cell_entry(sub_arr):
    arr = np.empty(3, dtype=object)
    arr[:] = [sub_arr, sub_arr, sub_arr]
    return arr

params_base = [
    (
        pd.DataFrame({"Var1": [1.1, 2.2, 3.3], "Var2": [4.4, 5.5, 6.6]}),
        "T1",
    ),
    (
        pd.DataFrame(
            {
                "Var1": ["apple", "banana", "cherry"],
            }
        ),
        "T2",
    ),
    (
        pd.DataFrame(
            {
                "Time": np.array(
                    [
                        "2020-01-01T00:00:00.000",
                        "2020-01-02T00:00:00.000",
                        "2020-01-03T00:00:00.000",
                    ],
                    dtype="datetime64[ms]",
                ),
                "Duration": np.array([30, 60, 90], dtype="timedelta64[s]"),
            }
        ),
        "T3",
    ),
    (
        pd.DataFrame(
            {
                "Var1": [
                    np.array([[1.0]]),
                    np.array(["text"]),
                    np.array([["2023-01-01T00:00:00.000"]], dtype="datetime64[ms]"),
                ],
            }
        ),
        "T5",
    ),
    (
        pd.DataFrame(
            {
                "Var1": [1.1, np.nan, 3.3],
                "Var2": np.array(["A", "", "C"]),
            }
        ),
        "T6",
    ),
    (
        pd.DataFrame(
            {
                "X": np.array([10.0, 20.0, 30.0]),
                "Y": np.array([100.0, 200.0, 300.0]),
            }
        ),
        "T7",
    ),
    (
        pd.DataFrame(
            {
                "Col1": np.array([1.0, 2.0, 3.0]),
                "Col2": np.array([4.0, 5.0, 6.0]),
            },
            index=["R1", "R2", "R3"],
        ),
        "T8",
    ),
    (
        pd.DataFrame(
            {
                "Var1": np.array(
                    [
                        "2023-01-01T00:00:00.000",
                        "2023-01-02T00:00:00.000",
                        "2023-01-03T00:00:00.000",
                    ],
                    dtype="datetime64[ms]",
                ),
                "data_1": np.array([1.0, 2.0, 3.0]),
                "data_2": np.array([4.0, 5.0, 6.0]),
            }
        ),
        "T10",
    ),
]

params_obj = [
    (
        pd.DataFrame(
            {
                "C": make_cell_entry(
                    np.array(
                        [[(np.array([[123.0]]), np.array(["abc"]))]],
                        dtype=[("field1", "O"), ("field2", "O")],
                    )
                ),
                "Var2": make_cell_entry(
                    {
                        "_Class": "MyObj",
                        "_Props": np.array(
                            [[{"Value": np.array([[42.0]])}]], dtype=object
                        ),
                    }
                ),
            }
        ),
        "T4",
    )
]

params_attrs = [
    (
        pd.DataFrame(
            {
                "ID": np.array([1.0, 2.0]),
                "Label": np.array(["one", "two"]),
            }
        ),
        "T9",
    ),
]

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_base,
    ids=[
        "simple-table-v7",
        "table-with-strings-v7",
        "table-with-datetime-v7",
        "table-with-mixed-types-v7",
        "table-with-nan-v7",
        "table-with-row-names-v7",
        "table-with-row-names-v7",
        "table-with-multicolumn-var-v7",
    ],
)
def test_table_read_v7(expected_df, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_table_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_base,
    ids=[
        "simple-table-v7.3",
        "table-with-strings-v7.3",
        "table-with-datetime-v7.3",
        "table-with-mixed-types-v7.3",
        "table-with-nan-v7.3",
        "table-with-row-names-v7.3",
        "table-with-row-names-v7.3",
        "table-with-multicolumn-var-v7.3",
    ],
)
def test_table_read_v73(expected_df, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_table_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)


@pytest.mark.parametrize(
    "expected_df, var_name",
    params_obj,
    ids=["table-with-struct-and-object-v7"],
)
def test_table_struct_and_object_read_v7(expected_df, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_table_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)
    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_obj,
    ids=["table-with-struct-and-object-v7.3"],
)
def test_table_struct_and_object_read_v73(expected_df, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_table_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)
    assert var_name in matdict
    pd.testing.assert_frame_equal(matdict[var_name], expected_df)

@pytest.mark.parametrize(
    "expected_df, var_name",
    params_attrs,
    ids=["table-with-attrs-v7"],
)
def test_table_with_attrs_read_v7(expected_df, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_table_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False, add_table_attrs=True)
    expected_df.attrs = {
        "Description": "Test table with full metadata",
        "DimensionNames": ["RowId", "Features"],
        "VariableUnits": ["", "category"],
        "VariableDescriptions": ["ID number", "Category label"],
        "VariableContinuity": ["continuous", "step"],
        "UserData": np.array(
            [[(np.array(["UnitTest"]), np.array([[1.0]]))]],
            dtype=[("CreatedBy", "O"), ("Version", "O")],
        ),
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
    params_attrs,
    ids=["table-with-attrs-v7.3"],
)
def test_table_with_attrs_read_v73(expected_df, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_table_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False, add_table_attrs=True)
    expected_df.attrs = {
        "Description": "Test table with full metadata",
        "DimensionNames": ["RowId", "Features"],
        "VariableUnits": ["", "category"],
        "VariableDescriptions": ["ID number", "Category label"],
        "VariableContinuity": ["continuous", "step"],
        "UserData": np.array(
            [[(np.array(["UnitTest"]), np.array([[1.0]]))]],
            dtype=[("CreatedBy", "O"), ("Version", "O")],
        ),
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
