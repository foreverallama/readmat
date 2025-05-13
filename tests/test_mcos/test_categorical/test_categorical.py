import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        np.array(["blue", "green", "red"]),
        np.array([[2, 1, 0, 2]]),
        False,
        "cat1",
    ),
    (
        np.array(["high", "low", "medium"]),
        np.array([[1, 2], [0, 1]]),
        False,
        "cat2",
    ),
    (
        np.array(["cold", "warm", "hot"]),
        np.array([[0, 2, 1]]),
        False,
        "cat3",
    ),
    (
        np.array(["small", "medium", "large"]),
        np.array([[0, 1, 2]]),
        True,
        "cat4",
    ),
    (
        np.array(["low", "medium", "high"]),
        np.array([[0, 1, 2, 1, 0]]),
        False,
        "cat5",
    ),
    (
        [],
        np.empty((0, 0), dtype=np.uint8),
        False,
        "cat6",
    ),
    (
        np.array(["cat", "dog", "mouse"]),
        np.array([[0, -1, 1, 2]]),
        False,
        "cat7",
    ),
    (
        np.array(["autumn", "spring", "summer", "winter"]),
        np.array([[1, 2, 0, 3]]),
        False,
        "cat8",
    ),
    (
        np.array(["OFF", "ON", "On", "off", "on"]),
        np.array([[2, 3, 0, 1, 4]]),
        False,
        "cat9",
    ),
    (
        np.array(["maybe", "no", "yes"]),
        np.tile(np.array([[2, 2], [1, 1], [0, 0]], dtype=np.uint8), (2, 1, 1)),
        False,
        "cat10",
    ),
]

@pytest.mark.parametrize(
    "categories, codes, ordered, var_name",
    params,
    ids=[
        "categorical-basic-v7",
        "categorical-2D-v7",
        "categorical-explicit-cats-v7",
        "categorical-ordered-v7",
        "categorical-numeric-labels-v7",
        "categorical-empty-v7",
        "categorical-missing-labels-v7",
        "categorical-from-string-v7",
        "categorical-mixed-case-cats-v7",
        "categorical-3D-v7",
    ],
)
def test_categorical_read_v7(categories, codes, ordered, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_categorical_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)
    assert var_name in matdict
    assert np.array_equal(matdict[var_name].codes, codes)
    assert np.array_equal(matdict[var_name].categories, categories)
    assert np.array_equal(matdict[var_name].ordered, ordered)

@pytest.mark.parametrize(
    "categories, codes, ordered, var_name",
    params,
    ids=[
        "categorical-basic-v7.3",
        "categorical-2D-v7.3",
        "categorical-explicit-cats-v7.3",
        "categorical-ordered-v7.3",
        "categorical-numeric-labels-v7.3",
        "categorical-empty-v7.3",
        "categorical-missing-labels-v7.3",
        "categorical-from-string-v7.3",
        "categorical-mixed-case-cats-v7.3",
        "categorical-3D-v7.3",
    ],
)
def test_categorical_read_v73(categories, codes, ordered, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_categorical_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)
    assert var_name in matdict
    assert np.array_equal(matdict[var_name].codes, codes)
    assert np.array_equal(matdict[var_name].categories, categories)
    assert np.array_equal(matdict[var_name].ordered, ordered)
