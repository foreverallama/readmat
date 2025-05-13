import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        np.array(["Hello"], dtype=np.str_).reshape(1, 1),
        "s1",
    ),
    (
        np.array(
            ["Apple", "Banana", "Cherry", "Date", "Fig", "Grapes"], dtype=np.str_
        ).reshape(2, 3),
        "s2",
    ),
    (
        np.array([""], dtype=np.str_).reshape(1, 1),
        "s3",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=["simple-string-v7", "string-array-v7", "empty-string-v7"],
)
def test_string_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_string_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=["simple-string-v7.3", "string-array-v7.3", "empty-string-v7.3"],
)
def test_string_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_string_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
