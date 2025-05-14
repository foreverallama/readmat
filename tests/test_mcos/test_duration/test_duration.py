import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        np.array([5], dtype="timedelta64[s]").reshape(1, 1),
        "dur1",
    ),
    (
        np.array([5], dtype="timedelta64[m]").reshape(1, 1),
        "dur2",
    ),
    (
        np.array([5], dtype="timedelta64[h]").reshape(1, 1),
        "dur3",
    ),
    (
        np.array([5], dtype="timedelta64[D]").reshape(1, 1),
        "dur4",
    ),
    (
        np.array([1, 2, 3], dtype="timedelta64[Y]").reshape(1, 3),
        "dur8",
    ),
    (
        (np.timedelta64(1, "h") + np.timedelta64(2, "m") + np.timedelta64(3, "s"))
        .astype("timedelta64[ms]")
        .reshape(1, 1),
        "dur5",
    ),
    (
        np.array([10, 20, 30, 40, 50, 60], dtype="timedelta64[s]").reshape(2, 3),
        "dur6",
    ),
    (
        np.array([], dtype="datetime64[ms]"),
        "dur7",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "duration-seconds-v7",
        "duration-minutes-v7",
        "duration-hours-v7",
        "duration-days-v7",
        "duration-years-v7",
        "duration-base-v7",
        "duration-array-v7",
        "duration-empty-v7",
    ],
)
def test_duration_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_duration_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "duration-seconds-v7.3",
        "duration-minutes-v7.3",
        "duration-hours-v7.3",
        "duration-days-v7.3",
        "duration-years-v7.3",
        "duration-base-v7.3",
        "duration-array-v7.3",
        "duration-empty-v7.3",
    ],
)
def test_duration_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_duration_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
