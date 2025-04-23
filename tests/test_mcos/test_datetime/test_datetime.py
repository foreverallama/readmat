import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array([["2025-04-01T12:00:00"]], dtype="datetime64[ms]").reshape(1, 1),
            "dt_base.mat",
            "dt1",
        ),
        (
            np.array([["2025-04-01T12:00:00"]], dtype="datetime64[ms]").reshape(1, 1),
            "dt_tz.mat",
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
            "dt_array.mat",
            "dt3",
        ),
        (
            np.array([], dtype="datetime64[ms]"),
            "dt_empty.mat",
            "dt4",
        ),
    ],
    ids=[
        "datetime-basic",
        "datetime-timezone",
        "datetime-array",
        "datetime-empty",
    ],
)
def test_load_datetime(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
