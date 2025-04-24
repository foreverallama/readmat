import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            (
                np.empty((0, 0), dtype="timedelta64[M]"),
                np.empty((0, 0), dtype="timedelta64[D]"),
                np.empty((0, 0), dtype="timedelta64[ms]"),
            ),
            "cdur1.mat",
            "cdur1",
        ),
        (
            (
                np.array([[0]], dtype="timedelta64[M]"),
                np.array([[1, 2, 3]], dtype="timedelta64[D]"),
                np.array([[0]], dtype="timedelta64[ms]"),
            ),
            "cdur2.mat",
            "cdur2",
        ),
        (
            (
                np.array([[0]], dtype="timedelta64[M]"),
                np.array([[7, 14]], dtype="timedelta64[D]"),
                np.array([[0]], dtype="timedelta64[ms]"),
            ),
            "cdur3.mat",
            "cdur3",
        ),
        (
            (
                np.array([[1, 0]], dtype="timedelta64[M]"),
                np.array([[1, 2]], dtype="timedelta64[D]"),
                np.array([[0]], dtype="timedelta64[ms]"),
            ),
            "cdur4.mat",
            "cdur4",
        ),
        (
            (
                np.array([[12, 18]], dtype="timedelta64[M]"),
                np.array([[0]], dtype="timedelta64[D]"),
                np.array([[0]], dtype="timedelta64[ms]"),
            ),
            "cdur5.mat",
            "cdur5",
        ),
        (
            (
                np.array([[3]], dtype="timedelta64[M]"),
                np.array([[15]], dtype="timedelta64[D]"),
                np.array([[0]], dtype="timedelta64[ms]"),
            ),
            "cdur6.mat",
            "cdur6",
        ),
        (
            (
                np.array([[1, 0], [2, 0]], dtype="timedelta64[M]"),
                np.array([[0, 5], [0, 10]], dtype="timedelta64[D]"),
                np.array([[0, 0], [0, 0]], dtype="timedelta64[ms]"),
            ),
            "cdur7.mat",
            "cdur7",
        ),
        (
            (
                np.array([[0]], dtype="timedelta64[M]"),
                np.array([[1]], dtype="timedelta64[D]"),
                np.array([[3723000]], dtype="timedelta64[ms]"),
            ),
            "cdur8.mat",
            "cdur8",
        ),
    ],
    ids=[
        "calendarDuration-empty",
        "calendarDuration-days",
        "calendarDuration-weeks",
        "calendarDuration-mixed",
        "calendarDuration-years",
        "calendarDuration-quarters",
        "calendarDuration-2D",
        "calendarDuration-duration",
    ],
)
def test_load_duration(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    actual_tup = matdict[var_name][0, 0]["calendarDuration"]
    assert np.array_equal(actual_tup[0], expected_array[0])
    assert np.array_equal(actual_tup[1], expected_array[1])
    assert np.array_equal(actual_tup[2], expected_array[2])
