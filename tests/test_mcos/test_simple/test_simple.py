import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (np.array([10]).reshape(1, 1), "var_int.mat", "var_int"),
    ],
    ids=["simple-string"],
)
def test_parse_no_object(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name] == expected_array

    assert isinstance(matdict[var_name], np.ndarray)
    np.testing.assert_array_equal(matdict[var_name], expected_array)


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array(
                [
                    np.array(["String in Cell"]).reshape(1, 1),
                ]
            ).reshape(1, 1),
            "var_cell.mat",
            "var_cell",
        ),
    ],
    ids=["string-in-cell"],
)
def test_parse_string_in_cell(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert isinstance(matdict[var_name], np.ndarray)
    np.testing.assert_array_equal(matdict[var_name], expected_array)


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array(
                [[(np.array(["String in Struct"]).reshape(1, 1),)]],
                dtype=[("MyField", "O")],
            ),
            "var_struct.mat",
            "var_struct",
        )
    ],
    ids=["string-in-struct"],
)
def test_parse_string_in_struct(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)
    print(matdict[var_name])
    print(expected_array)
    # Output format
    assert var_name in matdict
    assert isinstance(matdict[var_name], np.ndarray)
    np.testing.assert_array_equal(matdict[var_name], expected_array)
