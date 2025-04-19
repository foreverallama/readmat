import os

import numpy as np
import pytest

from matio import load_from_mat


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "EnumClass",
                "_BuiltinClassName": None,
                "_Tag": "EnumerationInstance",
                "_ValueNames": np.array(["enum1"]).reshape(1, 1),
                "_Values": np.array(
                    [
                        {
                            "val": np.array([1]).reshape(1, 1),
                        }
                    ]
                ).reshape(1, 1),
            },
            "enum_base.mat",
            "enum_base",
        ),
        (
            {
                "_Class": "EnumClass",
                "_BuiltinClassName": None,
                "_Tag": "EnumerationInstance",
                "_ValueNames": np.array(
                    ["enum1", "enum3", "enum5", "enum2", "enum4", "enum6"]
                ).reshape(2, 3),
                "_Values": np.array(
                    [
                        {
                            "val": np.array([1]).reshape(1, 1),
                        },
                        {
                            "val": np.array([3]).reshape(1, 1),
                        },
                        {
                            "val": np.array([5]).reshape(1, 1),
                        },
                        {
                            "val": np.array([2]).reshape(1, 1),
                        },
                        {
                            "val": np.array([4]).reshape(1, 1),
                        },
                        {
                            "val": np.array([6]).reshape(1, 1),
                        },
                    ]
                ).reshape(2, 3),
            },
            "enum_array.mat",
            "enum_arr",
        ),
        (
            {
                "_Class": "EnumClass2",
                "_BuiltinClassName": "uint32",
                "_Tag": "EnumerationInstance",
                "_ValueNames": np.array(["enum1"]).reshape(1, 1),
                "_Values": np.array(
                    [
                        {
                            "uint32.Data": np.array([1]).reshape(1, 1),
                        },
                    ]
                ).reshape(1, 1),
            },
            "enum_uint32.mat",
            "enum_uint32",
        ),
    ],
    ids=["enum-base", "enum-array", "enum-derived"],
)
def test_enum_instance(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].keys() == expected_array.keys()

    # Class Name
    assert matdict[var_name]["_Class"] == expected_array["_Class"]
    assert matdict[var_name]["_BuiltinClassName"] == expected_array["_BuiltinClassName"]

    # Value Names
    np.testing.assert_array_equal(
        matdict[var_name]["_ValueNames"], expected_array["_ValueNames"]
    )

    # Values
    assert matdict[var_name]["_Values"].shape == expected_array["_Values"].shape
    assert matdict[var_name]["_Values"].dtype == expected_array["_Values"].dtype
    for idx in np.ndindex(expected_array["_Values"].shape):
        expected_props = expected_array["_Values"][idx]
        actual_props = matdict[var_name]["_Values"][idx]
        for prop, val in expected_props.items():
            np.testing.assert_array_equal(actual_props[prop], val)


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "NestedClass",
                "_Props": np.array(
                    {
                        "objProp": {
                            "_Class": "EnumClass",
                            "_BuiltinClassName": None,
                            "_Tag": "EnumerationInstance",
                            "_ValueNames": np.array(["enum1"]).reshape(1, 1),
                            "_Values": np.array(
                                [
                                    {
                                        "val": np.array([1]).reshape(1, 1),
                                    }
                                ]
                            ).reshape(1, 1),
                        },
                        "cellProp": np.array(
                            [
                                [
                                    {
                                        "_Class": "EnumClass",
                                        "_BuiltinClassName": None,
                                        "_Tag": "EnumerationInstance",
                                        "_ValueNames": np.array(["enum2"]).reshape(
                                            1, 1
                                        ),
                                        "_Values": np.array(
                                            [
                                                {
                                                    "val": np.array([2]).reshape(1, 1),
                                                }
                                            ]
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
                                        "_Class": "EnumClass",
                                        "_BuiltinClassName": None,
                                        "_Tag": "EnumerationInstance",
                                        "_ValueNames": np.array(["enum3"]).reshape(
                                            1, 1
                                        ),
                                        "_Values": np.array(
                                            [
                                                {
                                                    "val": np.array([3]).reshape(1, 1),
                                                }
                                            ]
                                        ).reshape(1, 1),
                                    }
                                ]
                            ],
                            dtype=[("ObjField", "O")],
                        ),
                    }
                ).reshape(1, 1),
            },
            "enum_inside_obj.mat",
            "obj1",
        )
    ],
    ids=["enum-inside-object"],
)
def test_enum_inside_object(expected_array, file_name, var_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].keys() == expected_array.keys()

    # Class Name
    assert matdict[var_name]["_Class"] == expected_array["_Class"]

    # Props Array
    assert matdict[var_name]["_Props"].shape == expected_array["_Props"].shape
    assert matdict[var_name]["_Props"].dtype == expected_array["_Props"].dtype

    # Props Dict
    actual_props = matdict[var_name]["_Props"][0, 0]
    expected_props = expected_array["_Props"][0, 0]
    for prop, val in expected_props.items():
        if prop == "cellProp":
            nested_actual_dict = actual_props[prop][0, 0]
            nested_expected_dict = val[0, 0]
            print(nested_actual_dict)
            print(nested_expected_dict)
            # Class Name
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_BuiltinClassName"]
                == nested_expected_dict["_BuiltinClassName"]
            )

            # Value Names
            np.testing.assert_array_equal(
                nested_actual_dict["_ValueNames"], nested_expected_dict["_ValueNames"]
            )

            # Values
            assert (
                nested_actual_dict["_Values"].shape
                == nested_expected_dict["_Values"].shape
            )
            assert (
                nested_actual_dict["_Values"].dtype
                == nested_expected_dict["_Values"].dtype
            )
            for idx in np.ndindex(nested_expected_dict["_Values"].shape):
                expected_sub_props = nested_expected_dict["_Values"][idx]
                actual_sub_props = nested_actual_dict["_Values"][idx]
                for prop, val in expected_sub_props.items():
                    np.testing.assert_array_equal(actual_sub_props[prop], val)

        elif prop == "structProp":
            nested_actual_dict = actual_props[prop]["ObjField"][0, 0]
            nested_expected_dict = val["ObjField"][0, 0]
            print(nested_actual_dict)
            print(nested_expected_dict)

            # Class Name
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_BuiltinClassName"]
                == nested_expected_dict["_BuiltinClassName"]
            )

            # Value Names
            np.testing.assert_array_equal(
                nested_actual_dict["_ValueNames"], nested_expected_dict["_ValueNames"]
            )

            # Values
            assert (
                nested_actual_dict["_Values"].shape
                == nested_expected_dict["_Values"].shape
            )
            assert (
                nested_actual_dict["_Values"].dtype
                == nested_expected_dict["_Values"].dtype
            )
            for idx in np.ndindex(nested_expected_dict["_Values"].shape):
                expected_sub_props = nested_expected_dict["_Values"][idx]
                actual_sub_props = nested_actual_dict["_Values"][idx]
                for prop, val in expected_sub_props.items():
                    np.testing.assert_array_equal(actual_sub_props[prop], val)

        elif prop == "objProp":
            nested_actual_dict = actual_props[prop]
            nested_expected_dict = val

            # Class Name
            assert nested_actual_dict["_Class"] == nested_expected_dict["_Class"]
            assert (
                nested_actual_dict["_BuiltinClassName"]
                == nested_expected_dict["_BuiltinClassName"]
            )

            # Value Names
            np.testing.assert_array_equal(
                nested_actual_dict["_ValueNames"], nested_expected_dict["_ValueNames"]
            )

            # Values
            assert (
                nested_actual_dict["_Values"].shape
                == nested_expected_dict["_Values"].shape
            )
            assert (
                nested_actual_dict["_Values"].dtype
                == nested_expected_dict["_Values"].dtype
            )
            for idx in np.ndindex(nested_expected_dict["_Values"].shape):
                expected_sub_props = nested_expected_dict["_Values"][idx]
                actual_sub_props = nested_actual_dict["_Values"][idx]
                for prop, val in expected_sub_props.items():
                    np.testing.assert_array_equal(actual_sub_props[prop], val)
