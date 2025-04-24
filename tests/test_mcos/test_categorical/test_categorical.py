import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "categories, codes, ordered, file_name, var_name",
    [
        (
            np.array(["blue", "green", "red"]),
            np.array([[2, 1, 0, 2]]),
            False,
            "cat1.mat",
            "cat1",
        ),
        (
            np.array(["high", "low", "medium"]),
            np.array([[1, 2], [0, 1]]),
            False,
            "cat2.mat",
            "cat2",
        ),
        (
            np.array(["cold", "warm", "hot"]),
            np.array([[0, 2, 1]]),
            False,
            "cat3.mat",
            "cat3",
        ),
        (
            np.array(["small", "medium", "large"]),
            np.array([[0, 1, 2]]),
            True,
            "cat4.mat",
            "cat4",
        ),
        (
            np.array(["low", "medium", "high"]),
            np.array([[0, 1, 2, 1, 0]]),
            False,
            "cat5.mat",
            "cat5",
        ),
        (
            [],
            np.empty((0, 0), dtype=np.uint8),
            False,
            "cat6.mat",
            "cat6",
        ),
        (
            np.array(["cat", "dog", "mouse"]),
            np.array([[0, -1, 1, 2]]),
            False,
            "cat7.mat",
            "cat7",
        ),
        (
            np.array(["autumn", "spring", "summer", "winter"]),
            np.array([[1, 2, 0, 3]]),
            False,
            "cat8.mat",
            "cat8",
        ),
        (
            np.array(["OFF", "ON", "On", "off", "on"]),
            np.array([[2, 3, 0, 1, 4]]),
            False,
            "cat9.mat",
            "cat9",
        ),
        (
            np.array(["maybe", "no", "yes"]),
            np.tile(np.array([[2, 2], [1, 1], [0, 0]], dtype=np.uint8), (2, 1, 1)),
            False,
            "cat10.mat",
            "cat10",
        ),
    ],
    ids=[
        "categorical-basic",
        "categorical-2D",
        "categorical-explicit-cats",
        "categorical-ordered",
        "categorical-numeric-labels",
        "categorical-empty",
        "categorical-missing-labels",
        "categorical-from-string",
        "categorical-mixed-case-cats",
        "categorical-3D",
    ],
)
def test_load_categorical(categories, codes, ordered, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)
    assert var_name in matdict
    assert np.array_equal(matdict[var_name].codes, codes)
    assert np.array_equal(matdict[var_name].categories, categories)
    assert np.array_equal(matdict[var_name].ordered, ordered)
