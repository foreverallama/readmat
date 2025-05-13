import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        (
            np.empty((0, 0), dtype="timedelta64[M]"),
            np.empty((0, 0), dtype="timedelta64[D]"),
            np.empty((0, 0), dtype="timedelta64[ms]"),
        ),
        "cdur1",
    ),
    (
        (
            np.array([[0]], dtype="timedelta64[M]"),
            np.array([[1, 2, 3]], dtype="timedelta64[D]"),
            np.array([[0]], dtype="timedelta64[ms]"),
        ),
        "cdur2",
    ),
    (
        (
            np.array([[0]], dtype="timedelta64[M]"),
            np.array([[7, 14]], dtype="timedelta64[D]"),
            np.array([[0]], dtype="timedelta64[ms]"),
        ),
        "cdur3",
    ),
    (
        (
            np.array([[1, 0]], dtype="timedelta64[M]"),
            np.array([[1, 2]], dtype="timedelta64[D]"),
            np.array([[0]], dtype="timedelta64[ms]"),
        ),
        "cdur4",
    ),
    (
        (
            np.array([[12, 18]], dtype="timedelta64[M]"),
            np.array([[0]], dtype="timedelta64[D]"),
            np.array([[0]], dtype="timedelta64[ms]"),
        ),
        "cdur5",
    ),
    (
        (
            np.array([[3]], dtype="timedelta64[M]"),
            np.array([[15]], dtype="timedelta64[D]"),
            np.array([[0]], dtype="timedelta64[ms]"),
        ),
        "cdur6",
    ),
    (
        (
            np.array([[1, 0], [2, 0]], dtype="timedelta64[M]"),
            np.array([[0, 5], [0, 10]], dtype="timedelta64[D]"),
            np.array([[0, 0], [0, 0]], dtype="timedelta64[ms]"),
        ),
        "cdur7",
    ),
    (
        (
            np.array([[0]], dtype="timedelta64[M]"),
            np.array([[1]], dtype="timedelta64[D]"),
            np.array([[3723000]], dtype="timedelta64[ms]"),
        ),
        "cdur8",
    ),
]

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "calendarDuration-empty-v7",
        "calendarDuration-days-v7",
        "calendarDuration-weeks-v7",
        "calendarDuration-mixed-v7",
        "calendarDuration-years-v7",
        "calendarDuration-quarters-v7",
        "calendarDuration-2D-v7",
        "calendarDuration-duration-v7",
    ],
)
def test_duration_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_caldur_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    actual_tup = matdict[var_name][0, 0]["calendarDuration"]
    assert np.array_equal(actual_tup[0], expected_array[0])
    assert np.array_equal(actual_tup[1], expected_array[1])
    assert np.array_equal(actual_tup[2], expected_array[2])

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "calendarDuration-empty-v7.3",
        "calendarDuration-days-v7.3",
        "calendarDuration-weeks-v7.3",
        "calendarDuration-mixed-v7.3",
        "calendarDuration-years-v7.3",
        "calendarDuration-quarters-v7.3",
        "calendarDuration-2D-v7.3",
        "calendarDuration-duration-v7.3",
    ],
)
def test_duration_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_caldur_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    actual_tup = matdict[var_name][0, 0]["calendarDuration"]
    assert np.array_equal(actual_tup[0], expected_array[0])
    assert np.array_equal(actual_tup[1], expected_array[1])
    assert np.array_equal(actual_tup[2], expected_array[2])
