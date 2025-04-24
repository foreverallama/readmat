import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "containers.Map",
                "_Props": {
                    1: np.array(["a"]),
                    2: np.array(["b"]),
                },
            },
            "map2.mat",
            "map2",
        ),
        (
            {
                "_Class": "containers.Map",
                "_Props": {
                    "a": np.array([[1]]),
                    "b": np.array([[2]]),
                },
            },
            "map3.mat",
            "map3",
        ),
        (
            {
                "_Class": "containers.Map",
                "_Props": {
                    "a": np.array([[1]]),
                    "b": np.array([[2]]),
                },
            },
            "map4.mat",
            "map4",
        ),
    ],
    ids=[
        "map-numeric-key",
        "map-char-key",
        "map-string-key",
    ],
)
def test_load_containermap(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    assert matdict[var_name]["_Class"] == expected_array["_Class"]
    for key in expected_array["_Props"]:
        assert key in matdict[var_name]["_Props"]
        assert np.array_equal(
            matdict[var_name]["_Props"][key], expected_array["_Props"][key]
        )


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "containers.Map",
                "_Props": {},
            },
            "map1.mat",
            "map1",
        ),
    ],
    ids=[
        "map-empty",
    ],
)
def test_load_empty_containermap(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    assert matdict[var_name]["_Class"] == expected_array["_Class"]
    assert matdict[var_name]["_Props"] == expected_array["_Props"]
