"""Base class for MAT-file reading and writing"""

from matio.matio5 import read_matfile5
from matio.matio7 import read_matfile7


def get_matfile_version(byte_data):
    """Reads subsystem MAT-file version and endianness
    Inputs
        1. ss_stream (BytesIO): Subsystem data stream
    Returns:
        1. v_major (int): Major version
        2. v_minor (int): Minor version
        3. byte_order (str): Endianness
    """

    maj_ind = int(byte_data[2] == b"I"[0])
    v_major = int(byte_data[maj_ind])
    v_minor = int(byte_data[1 - maj_ind])
    if v_major in (1, 2):
        return v_major, v_minor

    raise NotImplementedError(f"Unknown MAT-file version {v_major}.{v_minor}")


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

    with open(file_path, "rb") as f:
        f.seek(124)
        version_bytes = f.read(4)
        v_major, v_minor = get_matfile_version(version_bytes)

    if v_major == 1:
        matfile_dict = read_matfile5(
            file_path, raw_data, add_table_attrs, spmatrix, **kwargs
        )
    elif v_major == 2:
        matfile_dict = read_matfile7(
            file_path, raw_data, add_table_attrs, spmatrix, **kwargs
        )
    else:
        raise NotImplementedError(f"Unknown MAT-file version {v_major}.{v_minor}")

    # Update mdict if present
    if mdict is not None:
        mdict.update(matfile_dict)
    else:
        mdict = matfile_dict

    return mdict
