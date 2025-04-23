import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array([5], dtype="timedelta64[s]").reshape(1, 1),
            "dur_s.mat",
            "dur1",
        ),
        (
            np.array([5], dtype="timedelta64[m]").reshape(1, 1),
            "dur_m.mat",
            "dur2",
        ),
        (
            np.array([5], dtype="timedelta64[h]").reshape(1, 1),
            "dur_h.mat",
            "dur3",
        ),
        (
            np.array([5], dtype="timedelta64[D]").reshape(1, 1),
            "dur_d.mat",
            "dur4",
        ),
        (
            np.array([1, 2, 3], dtype="timedelta64[Y]").reshape(1, 3),
            "dur_y.mat",
            "dur8",
        ),
        (
            (np.timedelta64(1, "h") + np.timedelta64(2, "m") + np.timedelta64(3, "s"))
            .astype("timedelta64[ms]")
            .reshape(1, 1),
            "dur_base.mat",
            "dur5",
        ),
        (
            np.array([10, 20, 30, 40, 50, 60], dtype="timedelta64[s]").reshape(2, 3),
            "dur_array.mat",
            "dur6",
        ),
        (
            np.array([], dtype="datetime64[ms]"),
            "dur_empty.mat",
            "dur7",
        ),
    ],
    ids=[
        "duration-seconds",
        "duration-minutes",
        "duration-hours",
        "duration-days",
        "duration-years",
        "duration-base",
        "duration-array",
        "duration-empty",
    ],
)
def test_load_duration(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
