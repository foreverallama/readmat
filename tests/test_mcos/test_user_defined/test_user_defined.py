import os

import numpy as np
import pytest

from matio import load_from_mat

params_base = [
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
        "obj3",
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
        "obj6",
    ),
]

params_nested = [
    (
        {
            "_Class": "NestedClass",
            "_Props": np.array(
                {
                    "objProp": {
                        "_Class": "NoConstructor",
                        "_Props": np.array(
                            {
                                "a": np.array([]).reshape(0, 0),
                                "b": np.array([]).reshape(0, 0),
                                "c": np.array([]).reshape(0, 0),
                            }
                        ).reshape(1, 1),
                    },
                    "cellProp": np.array(
                        [
                            [
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
                            ]
                        ],
                        dtype=object,
                    ),
                    "structProp": np.array(
                        [
                            [
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
                            ]
                        ],
                        dtype=[("ObjField", "O")],
                    ),
                }
            ).reshape(1, 1),
        },
        "obj4",
    )
]

params_default = [
    (
        {
            "_Class": "DefaultClass2",
            "_Props": np.array(
                {
                    "a": np.array(["Default String"]).reshape(1, 1),
                    "b": np.array([10]).reshape(1, 1),
                    "c": np.array([30]).reshape(1, 1),
                }
            ).reshape(1, 1),
        },
        "obj7",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params_base,
    ids=[
        "object-without-constructor-v7",
        "object-with-constructor-v7",
        "object-with-default-v7",
        "object-array-v7",
    ],
)
def test_user_defined_read_v7(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v7.mat")
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

@pytest.mark.parametrize(
    "expected_array, var_name",
    params_base,
    ids=[
        "object-without-constructor-v7.3",
        "object-with-constructor-v7.3",
        "object-with-default-v7.3",
        "object-array-v7.3",
    ],
)
def test_user_defined_read_v73(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v73.mat")
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


@pytest.mark.parametrize(
    "expected_array, var_name",
    params_nested,
    ids=["nested-object-v7"],
)
def test_user_defined_nested_read_v7(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v7.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].keys() == expected_array.keys()

    # Class Name
    assert matdict[var_name]["_Class"] == expected_array["_Class"]

    # Property Dict
    assert matdict[var_name]["_Props"].shape == expected_array["_Props"].shape
    assert matdict[var_name]["_Props"].dtype == expected_array["_Props"].dtype

    # Each Property
    actual_props = matdict[var_name]["_Props"][0, 0]
    expected_props = expected_array["_Props"][0, 0]
    for prop, val in expected_props.items():
        if prop == "cellProp":
            nested_actual_dict = actual_props[prop][0, 0]
            nested_expected_dict = val[0, 0]
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )
            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val
        elif prop == "structProp":
            nested_actual_dict = actual_props[prop]["ObjField"][0, 0]
            nested_expected_dict = val["ObjField"][0, 0]
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )
            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val

        elif prop == "objProp":
            nested_actual_dict = actual_props[prop]
            nested_expected_dict = val

            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )

            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val

@pytest.mark.parametrize(
    "expected_array, var_name",
    params_nested,
    ids=["nested-object-v7.3"],
)
def test_user_defined_nested_read_v73(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v73.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].keys() == expected_array.keys()

    # Class Name
    assert matdict[var_name]["_Class"] == expected_array["_Class"]

    # Property Dict
    assert matdict[var_name]["_Props"].shape == expected_array["_Props"].shape
    assert matdict[var_name]["_Props"].dtype == expected_array["_Props"].dtype

    # Each Property
    actual_props = matdict[var_name]["_Props"][0, 0]
    expected_props = expected_array["_Props"][0, 0]
    for prop, val in expected_props.items():
        if prop == "cellProp":
            nested_actual_dict = actual_props[prop][0, 0]
            nested_expected_dict = val[0, 0]
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )
            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val
        elif prop == "structProp":
            nested_actual_dict = actual_props[prop]["ObjField"][0, 0]
            nested_expected_dict = val["ObjField"][0, 0]
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )
            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val

        elif prop == "objProp":
            nested_actual_dict = actual_props[prop]
            nested_expected_dict = val

            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_Props"].shape
                == nested_expected_dict["_Props"].shape
            )
            assert (
                nested_actual_dict["_Props"].dtype
                == nested_expected_dict["_Props"].dtype
            )

            nested_expected_props = nested_expected_dict["_Props"][0, 0]
            nested_actual_props = nested_actual_dict["_Props"][0, 0]
            for prop, val in nested_expected_props.items():
                if isinstance(val, np.ndarray):
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
                else:
                    assert nested_actual_props[prop] == val


@pytest.mark.parametrize(
    "expected_array, var_name",
    params_default,
    ids=["object-in-default-property-v7"],
)
def test_user_defined_with_default_property_read_v7(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v7.mat")
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
            if isinstance(val, np.ndarray):
                np.testing.assert_array_equal(actual_props[prop], val)
            elif isinstance(val, dict):
                nested_actual_dict = actual_props[prop]
                nested_expected_dict = val

                assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
                assert (
                    nested_actual_dict["_Props"].shape
                    == nested_expected_dict["_Props"].shape
                )
                assert (
                    nested_actual_dict["_Props"].dtype
                    == nested_expected_dict["_Props"].dtype
                )

                nested_expected_props = nested_expected_dict["_Props"][0, 0]
                nested_actual_props = nested_actual_dict["_Props"][0, 0]
                for prop, val in nested_expected_props.items():
                    np.testing.assert_array_equal(nested_actual_props[prop], val)

@pytest.mark.parametrize(
    "expected_array, var_name",
    params_default,
    ids=["object-in-default-property-v7.3"],
)
def test_user_defined_with_default_property_read_v73(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_user_defined_v73.mat")
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
            if isinstance(val, np.ndarray):
                np.testing.assert_array_equal(actual_props[prop], val)
            elif isinstance(val, dict):
                nested_actual_dict = actual_props[prop]
                nested_expected_dict = val

                assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
                assert (
                    nested_actual_dict["_Props"].shape
                    == nested_expected_dict["_Props"].shape
                )
                assert (
                    nested_actual_dict["_Props"].dtype
                    == nested_expected_dict["_Props"].dtype
                )

                nested_expected_props = nested_expected_dict["_Props"][0, 0]
                nested_actual_props = nested_actual_dict["_Props"][0, 0]
                for prop, val in nested_expected_props.items():
                    np.testing.assert_array_equal(nested_actual_props[prop], val)
