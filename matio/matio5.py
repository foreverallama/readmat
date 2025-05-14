"""Reads MAT-files v7 to v7.2 (MAT-file 5) and extracts variables including MATLAB objects"""

from io import BytesIO

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from matio.subsystem import SubsystemReader


def read_subsystem(
    ssdata,
    byte_order,
    mat_dtype,
    verify_compressed_data_integrity,
):
    """Reads subsystem data as a MAT-file stream
    Inputs
        1. ssdata (numpy.ndarray): Subsystem data from "__function_workspace__"
        2. kwargs: Additional arguments for scipy.io.loadmat
    Returns:
        subsystem data (numpy.ndarray): Parsed subsystem data
    """
    ss_stream = BytesIO(ssdata)

    ss_stream.seek(8)  # Skip subsystem header
    subsystem_reader = MatFile5Reader(
        ss_stream,
        byte_order=byte_order,
        mat_dtype=mat_dtype,
        verify_compressed_data_integrity=verify_compressed_data_integrity,
    )
    subsystem_reader.initialize_read()
    hdr, _ = subsystem_reader.read_var_header()
    try:
        res = subsystem_reader.read_var_array(hdr, process=False)
    except Exception as err:
        raise ValueError(f"Error reading subsystem data: {err}") from err

    return res


def find_opaque_dtype(arr, subsystem, path=()):
    """Recursively finds and replaces mxOPAQUE_CLASS objects in a numpy array
    with the corresponding MCOS object.

    This is a hacky solution to find mxOPAQUE_CLASS arrays inside struct arrays or cell arrays.
    """

    if not isinstance(arr, np.ndarray):
        return arr

    if arr.dtype == OPAQUE_DTYPE:
        type_system = arr[0]["_TypeSystem"]
        metadata = arr[0]["_Metadata"]
        return subsystem.read_mcos_object(metadata, type_system)

    if arr.dtype == object:
        # Iterate through cell arrays
        for idx in np.ndindex(arr.shape):
            cell_item = arr[idx]
            if cell_item.dtype == OPAQUE_DTYPE:
                type_system = cell_item[0]["_TypeSystem"]
                metadata = cell_item[0]["_Metadata"]
                arr[idx] = subsystem.read_mcos_object(metadata, type_system)
            else:
                find_opaque_dtype(cell_item, subsystem, path + (idx,))

    elif arr.dtype.names:
        # Iterate though struct array
        for idx in np.ndindex(arr.shape):
            for name in arr.dtype.names:
                field_val = arr[idx][name]
                if field_val.dtype == OPAQUE_DTYPE:
                    type_system = field_val[0]["_TypeSystem"]
                    metadata = field_val[0]["_Metadata"]
                    arr[idx][name] = subsystem.read_mcos_object(metadata, type_system)
                else:
                    find_opaque_dtype(field_val, subsystem, path + (idx, name))

    return arr


def read_matfile5(
    file_path,
    raw_data=False,
    add_table_attrs=False,
    spmatrix=True,
    byte_order=None,
    mat_dtype=False,
    chars_as_strings=True,
    verify_compressed_data_integrity=True,
    variable_names=None,
):
    """Loads variables from MAT-file < v7.3
    Calls scipy.io.loadmat to read the MAT-file and then processes the
    "__function_workspace__" variable to extract subsystem data.
    Inputs
        1. raw_data (bool): Whether to return raw data for objects
        2. add_table_attrs (bool): Add attributes to pandas DataFrame
        3. spmatrix (bool): Additional arguments for scipy.io.loadmat
        4. byte_order (str): Endianness
        5. mat_dtype (bool): Whether to load MATLAB data types
        6. chars_as_strings (bool): Whether to load character arrays as strings
        8. verify_compressed_data_integrity (bool): Whether to verify compressed data integrity
        9. variable_names (list): List of variable names to load
    Returns:
        1. matfile_dict (dict): Dictionary of loaded variables
    """

    if variable_names is not None:
        if isinstance(variable_names, str):
            variable_names = [variable_names, "__function_workspace__"]
        elif not isinstance(variable_names, list):
            raise TypeError("variable_names must be a string or a list of strings")
        else:
            variable_names.append("__function_workspace__")

    matfile_dict = loadmat(
        file_path,
        spmatrix=spmatrix,
        byte_order=byte_order,
        mat_dtype=mat_dtype,
        chars_as_strings=chars_as_strings,
        verify_compressed_data_integrity=verify_compressed_data_integrity,
        variable_names=variable_names,
    )
    ssdata = matfile_dict.pop("__function_workspace__", None)
    if ssdata is None:
        # No subsystem data in file
        return matfile_dict

    byte_order = "<" if ssdata[0, 2] == b"I"[0] else ">"

    ss_array = read_subsystem(
        ssdata,
        byte_order,
        mat_dtype,
        verify_compressed_data_integrity,
    )
    subsystem = SubsystemReader(byte_order, raw_data, add_table_attrs)
    subsystem.init_fields_v7(ss_array)

    for var, data in matfile_dict.items():
        if not isinstance(data, np.ndarray):
            continue
        matfile_dict[var] = find_opaque_dtype(data, subsystem)

    return matfile_dict
