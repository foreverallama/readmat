import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        [
            (np.float64(1), np.str_("apple")),
            (np.float64(2), np.str_("banana")),
            (np.float64(3), np.str_("cherry")),
        ],
        "dict1",
    ),
    (
        [
            (np.str_("x"), np.float64(10)),
            (np.str_("y"), np.float64(20)),
            (np.str_("z"), np.float64(30)),
        ],
        "dict2",
    ),
    (
        [
            (np.str_("name"), np.array([["Alice"]])),
            (np.str_("age"), np.array([[25]])),
        ],
        "dict3",
    ),
    (
        [
            (np.array([[1]]), np.str_("one")),
            (np.array([[2]]), np.str_("two")),
            (np.array([[3]]), np.str_("three")),
        ],
        "dict4",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "dict-numeric-key-v7",
        "dict-char-key-v7",
        "dict-mixed-val-v7",
        "dict-cell-key-v7",
    ],
)
def test_containermap_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_dict_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    for i, (expected_key, expected_val) in enumerate(expected_array):
        actual_key = matdict[var_name][i][0]
        actual_val = matdict[var_name][i][1]
        assert np.array_equal(actual_key, expected_key)
        assert np.array_equal(actual_val, expected_val)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "dict-numeric-key-v7.3",
        "dict-char-key-v7.3",
        "dict-mixed-val-v7.3",
        "dict-cell-key-v7.3",
    ],
)
def test_containermap_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_dict_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    for i, (expected_key, expected_val) in enumerate(expected_array):
        actual_key = matdict[var_name][i][0]
        actual_val = matdict[var_name][i][1]
        assert np.array_equal(actual_key, expected_key)
        assert np.array_equal(actual_val, expected_val)
