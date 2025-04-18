import os

import numpy as np
import pytest

from readmat import load_from_mat


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
                    {
                        "_Class": "string",
                        "_Props": np.array(
                            [{"any": np.array(["String in Cell"]).reshape(1, 1)}]
                        ).reshape(1, 1),
                    },
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
    assert matdict[var_name].shape == expected_array.shape
    assert matdict[var_name].dtype == expected_array.dtype

    # Cell Content
    assert matdict[var_name][0, 0]["_Class"] == expected_array[0, 0]["_Class"]
    assert (
        matdict[var_name][0, 0]["_Props"].shape == expected_array[0, 0]["_Props"].shape
    )
    assert (
        matdict[var_name][0, 0]["_Props"].dtype == expected_array[0, 0]["_Props"].dtype
    )

    # Each property
    for prop, val in expected_array[0, 0]["_Props"][0, 0].items():
        np.testing.assert_array_equal(
            matdict[var_name][0, 0]["_Props"][0, 0][prop], val
        )


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array(
                [
                    {
                        "_Class": "string",
                        "_Props": np.array(
                            [{"any": np.array(["String in Struct"]).reshape(1, 1)}]
                        ).reshape(1, 1),
                    },
                ],
                dtype=[("MyField", "O")],
            ).reshape(1, 1),
            "var_struct.mat",
            "var_struct",
        )
    ],
    ids=["string-in-struct"],
)
def test_parse_string_in_struct(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert isinstance(matdict[var_name], np.ndarray)
    assert matdict[var_name].shape == expected_array.shape
    assert matdict[var_name].dtype == expected_array.dtype

    # Object
    expected_opaque_array = matdict[var_name][0, 0]["MyField"]
    actual_opaque_array = expected_array[0, 0]["MyField"]
    assert actual_opaque_array["_Class"] == expected_opaque_array["_Class"]
    assert actual_opaque_array["_Props"].shape == expected_opaque_array["_Props"].shape
    assert actual_opaque_array["_Props"].dtype == expected_opaque_array["_Props"].dtype

    # Each property
    for prop, val in expected_opaque_array["_Props"][0, 0].items():
        np.testing.assert_array_equal(actual_opaque_array["_Props"][0, 0][prop], val)
