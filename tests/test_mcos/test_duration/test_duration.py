import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array([5], dtype="timedelta64[s]").reshape(1, 1),
                        "fmt": np.array(["s"]),
                    }
                ).reshape(1, 1),
            },
            "dur_s.mat",
            "dur1",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array([5], dtype="timedelta64[m]").reshape(1, 1),
                        "fmt": np.array(["m"]),
                    }
                ).reshape(1, 1),
            },
            "dur_m.mat",
            "dur2",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array([5], dtype="timedelta64[h]").reshape(1, 1),
                        "fmt": np.array(["h"]),
                    }
                ).reshape(1, 1),
            },
            "dur_h.mat",
            "dur3",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array([5], dtype="timedelta64[D]").reshape(1, 1),
                        "fmt": np.array(["d"]),
                    }
                ).reshape(1, 1),
            },
            "dur_d.mat",
            "dur4",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": (
                            np.timedelta64(1, "h")
                            + np.timedelta64(2, "m")
                            + np.timedelta64(3, "s")
                        )
                        .astype("timedelta64[ms]")
                        .reshape(1, 1),
                        "fmt": np.array(["hh:mm:ss"]),
                    }
                ).reshape(1, 1),
            },
            "dur_base.mat",
            "dur5",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array(
                            [10, 20, 30, 40, 50, 60], dtype="timedelta64[s]"
                        ).reshape(2, 3),
                        "fmt": np.array(["s"]),
                    }
                ).reshape(1, 1),
            },
            "dur_array.mat",
            "dur6",
        ),
        (
            {
                "_Class": "duration",
                "_Props": np.array(
                    {
                        "millis": np.array([], dtype="datetime64[ms]"),
                        "fmt": np.array(["hh:mm:ss"]),
                    }
                ).reshape(1, 1),
            },
            "dur_empty.mat",
            "dur7",
        ),
    ],
    ids=[
        "duration-seconds",
        "duration-minutes",
        "duration-hours",
        "duration-days",
        "duration-base",
        "duration-array",
        "duration-empty",
    ],
)
def test_load_datetime(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].keys() == expected_array.keys()

    # Class Name
    assert matdict[var_name]["_Class"] == expected_array["_Class"]

    # Property Dict
    assert matdict[var_name]["_Props"].shape == expected_array["_Props"].shape
    assert matdict[var_name]["_Props"].dtype == expected_array["_Props"].dtype

    # Each property
    for prop, val in expected_array["_Props"][0, 0].items():
        np.testing.assert_array_equal(matdict[var_name]["_Props"][0, 0][prop], val)
