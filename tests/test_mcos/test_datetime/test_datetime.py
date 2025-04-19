import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "datetime",
                "_Props": np.array(
                    {
                        "data": np.array(
                            [["2025-04-01T12:00:00"]], dtype="datetime64[ms]"
                        ).reshape(1, 1),
                        "fmt": np.array([], dtype="U"),
                        "tz": np.array([], dtype="U"),
                    }
                ).reshape(1, 1),
            },
            "dt_base.mat",
            "dt1",
        ),
        (
            {
                "_Class": "datetime",
                "_Props": np.array(
                    {
                        "data": np.array(
                            [["2025-04-01T12:00:00"]], dtype="datetime64[ms]"
                        ).reshape(1, 1),
                        "fmt": np.array([], dtype="U"),
                        "tz": np.array(["America/New_York"]),
                    }
                ).reshape(1, 1),
            },
            "dt_tz.mat",
            "dt2",
        ),
        (
            {
                "_Class": "datetime",
                "_Props": np.array(
                    {
                        "data": np.array(
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
                        "fmt": np.array([], dtype="U"),
                        "tz": np.array([], dtype="U"),
                    }
                ).reshape(1, 1),
            },
            "dt_array.mat",
            "dt3",
        ),
        (
            {
                "_Class": "datetime",
                "_Props": np.array(
                    {
                        "data": np.array([], dtype="datetime64[ms]"),
                        "fmt": np.array([], dtype="U"),
                        "tz": np.array([], dtype="U"),
                    }
                ).reshape(1, 1),
            },
            "dt_empty.mat",
            "dt4",
        ),
        (
            {
                "_Class": "datetime",
                "_Props": np.array(
                    {
                        "data": np.array(
                            [["2025-04-01T12:00:00"]], dtype="datetime64[ms]"
                        ).reshape(1, 1),
                        "fmt": np.array(["yyyy-MM-dd HH:mm:ss"]),
                        "tz": np.array([], dtype="U"),
                    }
                ).reshape(1, 1),
            },
            "dt_fmt.mat",
            "dt5",
        ),
    ],
    ids=[
        "datetime-basic",
        "datetime-timezone",
        "datetime-array",
        "datetime-empty",
        "datetime-format",
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
