import os

import numpy as np
import pytest

from readmat import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "NoConstructor",
                "_Props": np.array(
                    {
                        "a": np.array([]).reshape(0, 0),
                        "b": np.array([]).reshape(0, 0),
                        "c": np.array([]).reshape(0, 0),
                    }
                ).reshape(1, 1),
            },
            "object_without_constructor.mat",
            "obj1",
        ),
        (
            {
                "_Class": "YesConstructor",
                "_Props": np.array(
                    {
                        "a": np.array([10]).reshape(1, 1),
                        "b": np.array([20]).reshape(1, 1),
                        "c": np.array([30]).reshape(1, 1),
                    }
                ).reshape(1, 1),
            },
            "object_with_constructor.mat",
            "obj2",
        ),
        (
            {
                "_Class": "DefaultClass",
                "_Props": np.array(
                    {
                        "a": np.array([]).reshape(0, 0),
                        "b": np.array([10]).reshape(1, 1),
                        "c": np.array([30]).reshape(1, 1),
                    }
                ).reshape(1, 1),
            },
            "object_with_default.mat",
            "obj3",
        ),
        (
            {
                "_Class": "NestedClass",
                "_Props": np.array(
                    {
                        "objProp": np.array(
                            {
                                "_Class": "NoConstructor",
                                "_Props": np.array(
                                    {
                                        "a": np.array([]).reshape(0, 0),
                                        "b": np.array([]).reshape(0, 0),
                                        "c": np.array([]).reshape(0, 0),
                                    }
                                ).reshape(1, 1),
                            }
                        ),
                        "cellProp": np.array(
                            [
                                [
                                    np.array(
                                        {
                                            "_Class": "YesConstructor",
                                            "_Props": np.array(
                                                {
                                                    "a": np.array([10]).reshape(1, 1),
                                                    "b": np.array([20]).reshape(1, 1),
                                                    "c": np.array([30]).reshape(1, 1),
                                                }
                                            ).reshape(1, 1),
                                        }
                                    )
                                ]
                            ],
                            dtype=object,
                        ),
                        "structProp": np.array(
                            [
                                [
                                    np.array(
                                        {
                                            "_Class": "DefaultClass",
                                            "_Props": np.array(
                                                {
                                                    "a": np.array([]).reshape(0, 0),
                                                    "b": np.array([10]).reshape(1, 1),
                                                    "c": np.array([30]).reshape(1, 1),
                                                }
                                            ).reshape(1, 1),
                                        }
                                    )
                                ]
                            ],
                            dtype=[("ObjField", "O")],
                        ),
                    }
                ).reshape(1, 1),
            },
            "nested_object.mat",
            "obj4",
        ),
        (
            {
                "_Class": "YesConstructor",
                "_Props": np.tile(
                    np.array(
                        {
                            "a": np.array([10]).reshape(1, 1),
                            "b": np.array([20]).reshape(1, 1),
                            "c": np.array([30]).reshape(1, 1),
                        }
                    ),
                    (2, 3),
                ),
            },
            "object_array.mat",
            "obj6",
        ),
    ],
    ids=[
        "object_without_constructor",
        "object_with_constructor",
        "object_with_default",
        "nested_object",
        "object_array",
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

    # Each property, user-defined are stored as MxN arrays unlike MATLAB datatypes
    for idx in np.ndindex(expected_array["_Props"].shape):
        expected_props = expected_array["_Props"][idx]
        actual_props = matdict[var_name]["_Props"][idx]
        for prop, val in expected_props.items():
            np.testing.assert_array_equal(actual_props[prop], val)
