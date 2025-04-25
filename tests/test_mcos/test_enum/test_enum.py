import os
from enum import Enum

import numpy as np
import pytest

from matio import load_from_mat


class EnumClass(Enum):
    """Enum class for testing purposes."""

    enum1 = {"val": np.array([1.0]).reshape(1, 1)}
    enum2 = {"val": np.array([2.0]).reshape(1, 1)}
    enum3 = {"val": np.array([3.0]).reshape(1, 1)}
    enum4 = {"val": np.array([4.0]).reshape(1, 1)}
    enum5 = {"val": np.array([5.0]).reshape(1, 1)}
    enum6 = {"val": np.array([6.0]).reshape(1, 1)}


class EnumClass2(Enum):
    """Enum class for testing"""

    enum1 = {"uint32.Data": np.array([1], dtype=np.uint32).reshape(1, 1)}


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            np.array(
                [
                    [
                        EnumClass.enum1,
                    ]
                ]
            ),
            "enum_base.mat",
            "enum_base",
        ),
        (
            np.array(
                [
                    EnumClass.enum1,
                    EnumClass.enum2,
                    EnumClass.enum3,
                    EnumClass.enum4,
                    EnumClass.enum5,
                    EnumClass.enum6,
                ]
            ).reshape(2, 3, order="F"),
            "enum_array.mat",
            "enum_arr",
        ),
        (
            np.array(
                [
                    [
                        EnumClass2.enum1,
                    ]
                ]
            ),
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
    assert matdict[var_name].shape == expected_array.shape
    assert matdict[var_name].dtype == expected_array.dtype

    for idx in np.ndindex(expected_array.shape):
        actual_member = matdict[var_name][idx]
        expected_member = expected_array[idx]
        assert actual_member.name == expected_member.name
        assert actual_member.value == expected_member.value


@pytest.mark.parametrize(
    "expected_array, file_name, var_name",
    [
        (
            {
                "_Class": "NestedClass",
                "_Props": np.array(
                    {
                        "objProp": np.array(
                            [
                                [
                                    EnumClass.enum1,
                                ]
                            ]
                        ),
                        "cellProp": np.array(
                            [
                                [
                                    np.array(
                                        [
                                            [
                                                EnumClass.enum2,
                                            ]
                                        ]
                                    )
                                ]
                            ],
                            dtype=object,
                        ),
                        "structProp": np.array(
                            [
                                [
                                    np.array(
                                        [
                                            [
                                                EnumClass.enum3,
                                            ]
                                        ]
                                    )
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
            nested_actual_member = actual_props[prop][0, 0][0, 0]
            nested_expected_member = val[0, 0][0, 0]
            assert nested_actual_member.name == nested_expected_member.name
            assert nested_actual_member.value == nested_expected_member.value

        elif prop == "structProp":
            nested_actual_member = actual_props[prop]["ObjField"][0, 0][0, 0]
            nested_expected_member = val["ObjField"][0, 0][0, 0]
            assert nested_actual_member.name == nested_expected_member.name
            assert nested_actual_member.value == nested_expected_member.value

        elif prop == "objProp":
            nested_actual_member = actual_props[prop][0, 0]
            nested_expected_member = val[0, 0]
            assert nested_actual_member.name == nested_expected_member.name
            assert nested_actual_member.value == nested_expected_member.value
