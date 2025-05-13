import os

import numpy as np
import pytest

from matio import load_from_mat

params = [
    (
        np.array([["2025-04-01T12:00:00"]], dtype="datetime64[ms]").reshape(1, 1),
        "dt1",
    ),
    (
        np.array([["2025-04-01T12:00:00"]], dtype="datetime64[ms]").reshape(1, 1),
        "dt2",
    ),
    (
        np.array(
            [
                [
                    "2025-04-01",
                    "2025-04-03",
                    "2025-04-05",
                    "2025-04-02",
                    "2025-04-04",
                    "2025-04-06",
                ]
            ],
            dtype="datetime64[ms]",
        ).reshape(2, 3),
        "dt3",
    ),
    (
        np.array([], dtype="datetime64[ms]"),
        "dt4",
    ),
]

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "datetime-basic-v7",
        "datetime-timezone-v7",
        "datetime-array-v7",
        "datetime-empty-v7",
    ],
)
def test_datetime_read_v7(expected_array, var_name):
    file_path_v7 = os.path.join(os.path.dirname(__file__), "test_datetime_v7.mat")
    matdict = load_from_mat(file_path_v7, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params,
    ids=[
        "datetime-basic-v7.3",
        "datetime-timezone-v7.3",
        "datetime-array-v7.3",
        "datetime-empty-v7.3",
    ],
)
def test_datetime_read_v73(expected_array, var_name):
    file_path_v73 = os.path.join(os.path.dirname(__file__), "test_datetime_v73.mat")
    matdict = load_from_mat(file_path_v73, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
