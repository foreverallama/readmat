import os

import numpy as np
import pytest
from scipy.io import loadmat

from matio import load_from_mat

basic_v7 = os.path.join(os.path.dirname(__file__), "basic_v7.mat")
basic_v73 = os.path.join(os.path.dirname(__file__), "basic_v73.mat")

v7_data = loadmat(basic_v7, mat_dtype=True)
variables = [(key, v7_data[key]) for key in v7_data.keys() if not key.startswith("__")]

@pytest.mark.parametrize(
    "var_name, expected",
    variables,
    ids = [v[0] for v in variables],
)
def test_v73_load_basic(var_name, expected):
    loaded_dict = load_from_mat(basic_v73)
    if isinstance(expected, np.ndarray):
        np.testing.assert_array_equal(
            loaded_dict[var_name], expected
        )
