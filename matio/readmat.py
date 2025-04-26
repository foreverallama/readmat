"""Reads MAT-files and extracts variables including MATLAB objects"""

from io import BytesIO

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from matio.subsystem import SubsystemReader


def get_matfile_version(ss_stream):
    """Reads subsystem MAT-file version and endianness
    Inputs
        1. ss_stream (BytesIO): Subsystem data stream
    Returns:
        1. v_major (int): Major version
        2. v_minor (int): Minor version
        3. byte_order (str): Endianness
    """

    ss_stream.seek(0)
    data = ss_stream.read(4)
    maj_ind = int(data[2] == b"I"[0])
    v_major = int(data[maj_ind])
    v_minor = int(data[1 - maj_ind])
    byte_order = "<" if data[2] == b"I"[0] else ">"
    if v_major in (1, 2):
        return v_major, v_minor, byte_order

    # Unsure if Subsystem and MAT-file versions can be different
    raise ValueError(f"Unknown subsystem data type, version {v_major}.{v_minor}")


def read_subsystem(ssdata, **kwargs):
    """Reads subsystem data as a MAT-file stream
    Inputs
        1. ssdata (numpy.ndarray): Subsystem data from "__function_workspace__"
        2. kwargs: Additional arguments for scipy.io.loadmat
    Returns:
        1. subsystem data (numpy.ndarray): Parsed subsystem data
        2. byte_order (str)
    """
    ss_stream = BytesIO(ssdata)

    mjv, mnv, byte_order = get_matfile_version(ss_stream)
    if mjv != 1:
        raise NotImplementedError(f"Subsystem version {mjv}.{mnv} not supported")

    kwargs.pop("byte_order", None)
    kwargs.pop("variable_names", None)

    ss_stream.seek(8)  # Skip subsystem header
    mat_reader = MatFile5Reader(ss_stream, byte_order=byte_order, **kwargs)
    mat_reader.initialize_read()
    hdr, _ = mat_reader.read_var_header()
    try:
        res = mat_reader.read_var_array(hdr, process=False)
    except Exception as err:
        raise ValueError(f"Error reading subsystem data: {err}") from err

    return res, byte_order


def remove_unsupported_args(kwargs):
    """Removes unsupported arguments for scipy.io.loadmat"""
    kwargs.pop("simplify_cells", None)
    kwargs.pop("squeeze_me", None)
    kwargs.pop("struct_as_record", None)
    kwargs.pop("uint16_codec", None)
    kwargs.pop("chars_as_strings", False)


def get_function_workspace(file_path, mdict=None, spmatrix=True, **kwargs):
    """Reads function workspace from MAT-file
    Inputs
        1. file_path (str): Path to MAT-file
        2. mdict (dict): Dictionary to store loaded variables
        3. spmatrix (bool): Whether to load sparse matrices
        4. kwargs: Additional arguments for scipy.io.loadmat
    Returns:
        1. matfile_dict (dict): Dictionary of loaded variables
        2. ssdata: Subsystem data from "__function_workspace__"
    """
    matfile_dict = loadmat(file_path, mdict=mdict, spmatrix=spmatrix, **kwargs)
    ssdata = matfile_dict.pop("__function_workspace__", None)
    return matfile_dict, ssdata


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


def load_from_mat(
    file_path,
    mdict=None,
    raw_data=False,
    add_table_attrs=False,
    *,
    spmatrix=True,
    **kwargs,
):
    """Loads variables from MAT-file
    Calls scipy.io.loadmat to read the MAT-file and then processes the
    "__function_workspace__" variable to extract subsystem data.
    Inputs
        1. file_path (str): Path to MAT-file
        2. mdict (dict): Dictionary to store loaded variables
        3. raw_data (bool): Whether to return raw data for objects
        4. add_table_attrs (bool): Add attributes to pandas DataFrame for MATLAB tables/timetables
        5. spmatrix (bool): Additional arguments for scipy.io.loadmat
        6. kwargs: Additional arguments for scipy.io.loadmat
    Returns:
        1. mdict (dict): Dictionary of loaded variables
    """

    remove_unsupported_args(kwargs)

    matfile_dict, ssdata = get_function_workspace(file_path, mdict, spmatrix, **kwargs)
    if ssdata is None:
        # No subsystem data in file
        if mdict is not None:
            mdict.update(matfile_dict)
            return mdict
        return matfile_dict

    ss_array, byte_order = read_subsystem(ssdata, **kwargs)
    subsystem = SubsystemReader(ss_array, byte_order, raw_data, add_table_attrs)

    for var, data in matfile_dict.items():
        if not isinstance(data, np.ndarray):
            continue
        matfile_dict[var] = find_opaque_dtype(data, subsystem)

    # Update mdict if present
    if mdict is not None:
        mdict.update(matfile_dict)
    else:
        mdict = matfile_dict

    return mdict
