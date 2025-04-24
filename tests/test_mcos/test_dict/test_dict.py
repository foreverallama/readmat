import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            [
                (np.float64(1), np.str_("apple")),
                (np.float64(2), np.str_("banana")),
                (np.float64(3), np.str_("cherry")),
            ],
            "dict1.mat",
            "dict1",
        ),
        (
            [
                (np.str_("x"), np.float64(10)),
                (np.str_("y"), np.float64(20)),
                (np.str_("z"), np.float64(30)),
            ],
            "dict2.mat",
            "dict2",
        ),
        (
            [
                (np.str_("name"), np.array([["Alice"]])),
                (np.str_("age"), np.array([[25]])),
            ],
            "dict3.mat",
            "dict3",
        ),
        (
            [
                (np.array([[1]]), np.str_("one")),
                (np.array([[2]]), np.str_("two")),
                (np.array([[3]]), np.str_("three")),
            ],
            "dict4.mat",
            "dict4",
        ),
    ],
    ids=[
        "dict-numeric-key",
        "dict-char-key",
        "dict-mixed-val",
        "dict-cell-key",
    ],
)
def test_load_containermap(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    for i, (expected_key, expected_val) in enumerate(expected_array):
        actual_key = matdict[var_name][i][0]
        actual_val = matdict[var_name][i][1]
        assert np.array_equal(actual_key, expected_key)
        assert np.array_equal(actual_val, expected_val)
