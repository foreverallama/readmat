import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array(["Hello"], dtype=np.str_).reshape(1, 1),
            "string_base.mat",
            "s1",
        ),
        (
            np.array(
                ["Apple", "Banana", "Cherry", "Date", "Fig", "Grapes"], dtype=np.str_
            ).reshape(2, 3),
            "string_array.mat",
            "s2",
        ),
        (
            np.array([""], dtype=np.str_).reshape(1, 1),
            "string_empty.mat",
            "s3",
        ),
    ],
    ids=["simple-string", "string-array", "empty-string"],
)
def test_parse_string(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    np.testing.assert_array_equal(matdict[var_name], expected_array)
