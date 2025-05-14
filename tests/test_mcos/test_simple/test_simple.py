import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        np.array([10]).reshape(1, 1),
        "var_int"
    ),
    (
        np.array(
            [
                np.array(["String in Cell"]).reshape(1, 1),
            ]
        ).reshape(1, 1),
        "var_cell",
    ),
    (
        np.array(
            [[(np.array(["String in Struct"]).reshape(1, 1),)]],
            dtype=[("MyField", "O")],
        ),
        "var_struct",
    ),
]

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=["simple-string-v7", "string-in-cell-v7","string-in-struct-v7"]
)
def test_simple_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_simple_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    # Output format
    assert var_name in matdict
    assert isinstance(matdict[var_name], np.ndarray)
    np.testing.assert_array_equal(matdict[var_name], expected_array)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=["simple-string-v7.3", "string-in-cell-v7.3","string-in-struct-v7.3"]
)
def test_simple_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_simple_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    # Output format
    assert var_name in matdict
    assert isinstance(matdict[var_name], np.ndarray)
    np.testing.assert_array_equal(matdict[var_name], expected_array)
