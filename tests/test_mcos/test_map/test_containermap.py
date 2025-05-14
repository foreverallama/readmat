import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        {
            "_Class": "containers.Map",
            "_Props": {},
        },
        "map1",
    ),
    (
        {
            "_Class": "containers.Map",
            "_Props": {
                1: np.array(["a"]),
                2: np.array(["b"]),
            },
        },
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
        "map4",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "map-empty-v7",
        "map-numeric-key-v7",
        "map-char-key-v7",
        "map-string-key-v7",
    ],
)
def test_containermap_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_map_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    assert matdict[var_name]["_Class"] == expected_array["_Class"]
    if not expected_array["_Props"]:
        assert matdict[var_name]["_Props"] == expected_array["_Props"]
    else:
        for key in expected_array["_Props"]:
            assert key in matdict[var_name]["_Props"]
            assert np.array_equal(
                matdict[var_name]["_Props"][key], expected_array["_Props"][key]
            )

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "map-empty-v7.3",
        "map-numeric-key-v7.3",
        "map-char-key-v7.3",
        "map-string-key-v7.3",
    ],
)
def test_containermap_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_map_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    assert matdict[var_name]["_Class"] == expected_array["_Class"]
    if not expected_array["_Props"]:
        assert matdict[var_name]["_Props"] == expected_array["_Props"]
    else:
        for key in expected_array["_Props"]:
            assert key in matdict[var_name]["_Props"]
            assert np.array_equal(
                matdict[var_name]["_Props"][key], expected_array["_Props"][key]
            )
