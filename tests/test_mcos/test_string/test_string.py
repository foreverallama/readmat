import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "string",
                "_Props": np.array(
                    {
                        "any": np.array(["Hello"]).reshape(1, 1),
                    }
                ).reshape(1, 1),
            },
            "string_base.mat",
            "s1",
        ),
        (
            {
                "_Class": "string",
                "_Props": np.array(
                    {
                        "any": np.array(
                            ["Apple", "Banana", "Cherry", "Date", "Fig", "Grapes"]
                        ).reshape(2, 3)
                    }
                ).reshape(1, 1),
            },
            "string_array.mat",
            "s2",
        ),
        (
            {
                "_Class": "string",
                "_Props": np.array({"any": np.array([""]).reshape(1, 1)}).reshape(1, 1),
            },
            "string_empty.mat",
            "s3",
        ),
    ],
    ids=["simple-string", "string-array", "empty-string"],
)
def test_parse_string_conditions(expected_array, file_name, var_name):
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
