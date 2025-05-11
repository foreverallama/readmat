import os

import numpy as np
import pytest
from scipy.io import loadmat

from matio import load_from_mat

sc_v7 = os.path.join(os.path.dirname(__file__), "struct_cell_v7.mat")
sc_v73 = os.path.join(os.path.dirname(__file__), "struct_cell_v73.mat")

v7_data = loadmat(sc_v7, mat_dtype=True)
variables = [(key, v7_data[key]) for key in v7_data.keys() if not key.startswith("__")]

def assert_mat_arrays_equal(actual, expected, name="var"):
    """
    Recursively assert equality between two MATLAB-like arrays (loaded as numpy arrays),
    handling nested object arrays (e.g., cells) and structured arrays (e.g., structs).
    """
    assert isinstance(actual, np.ndarray), f"{name}: actual is not a numpy array"
    assert isinstance(expected, np.ndarray), f"{name}: expected is not a numpy array"
    assert actual.shape == expected.shape, f"{name}: shape mismatch {actual.shape} != {expected.shape}"

    # Case 1: Structured array (MATLAB struct)
    if actual.dtype.names is not None and expected.dtype.names is not None:
        assert actual.dtype.names == expected.dtype.names, f"{name}: struct fields mismatch {actual.dtype.names} != {expected.dtype.names}"
        for field in actual.dtype.names:
            for idx in np.ndindex(actual.shape):
                subname = f"{name}[{idx}].{field}"
                act_val = actual[idx][field]
                exp_val = expected[idx][field]
                assert_mat_arrays_equal(np.asarray(act_val), np.asarray(exp_val), name=subname)

    # Case 2: Object array (e.g., cells or mixed struct/cell)
    elif actual.dtype == object or expected.dtype == object:
        for idx in np.ndindex(actual.shape):
            subname = f"{name}[{idx}]"
            act_val = actual[idx]
            exp_val = expected[idx]

            if isinstance(act_val, np.ndarray) and isinstance(exp_val, np.ndarray):
                assert_mat_arrays_equal(act_val, exp_val, name=subname)

            elif np.isscalar(act_val) and np.isscalar(exp_val):
                assert act_val == exp_val, f"{subname}: scalar mismatch {act_val} != {exp_val}"

            else:
                try:
                    np.testing.assert_array_equal(np.asarray(act_val), np.asarray(exp_val), err_msg=f"{subname}: mismatch")
                except Exception as e:
                    raise AssertionError(f"{subname}: object mismatch: {str(e)}")

    # Case 3: Regular arrays (numeric, string, etc.)
    else:
        try:
            np.testing.assert_array_equal(actual, expected, err_msg=f"{name}: array mismatch")
        except AssertionError as e:
            raise AssertionError(f"{name}: {str(e)}")

@pytest.mark.parametrize(
    "var_name, expected",
    variables,
    ids = [v[0] for v in variables],
)
def test_v7_load_struct_cell(var_name, expected):
    loaded_dict = load_from_mat(sc_v73)
    assert_mat_arrays_equal(loaded_dict[var_name], expected)
