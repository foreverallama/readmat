"""Utility functions for convertin MATLAB strings"""

import warnings

import numpy as np


def mat_to_string(props, byte_order):
    """Parse string data from MATLAB file
    String objects are stored as "any" properties in MAT-files.

    Strings are stored within a uint64 array with the following format:
        1. version
        2. ndims
        3. shape
        4. char_counts
        5. List of null-terminated strings as uint16 integers
    """

    data = props[0, 0].get("any", np.array([]))
    if data.size == 0:
        return np.array([[]], dtype=np.str_)

    if data[0, 0] != 1:
        warnings.warn(
            "String saved from a different MAT-file version. This may work unexpectedly",
            UserWarning,
        )

    ndims = data[0, 1]
    shape = data[0, 2 : 2 + ndims]
    num_strings = np.prod(shape)
    char_counts = data[0, 2 + ndims : 2 + ndims + num_strings]
    byte_data = data[0, 2 + ndims + num_strings :].tobytes()

    strings = []
    pos = 0
    encoding = "utf-16-le" if byte_order[0] == "<" else "utf-16-be"
    for char_count in char_counts:
        byte_length = char_count * 2  # UTF-16 encoding
        extracted_string = byte_data[pos : pos + byte_length].decode(encoding)
        strings.append(np.str_(extracted_string))
        pos += byte_length

    return np.reshape(strings, shape, order="F")
