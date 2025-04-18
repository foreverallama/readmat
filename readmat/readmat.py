import warnings
from io import BytesIO
from typing import Any, Dict, Tuple

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from .subsystem import SubsystemReader


def get_matfile_version(ssStream: BytesIO) -> Tuple[int, int, str]:
    """Reads subsystem byte order"""

    ssStream.seek(0)
    data = ssStream.read(4)
    ssStream.seek(0)
    maj_ind = int(data[2] == b"I"[0])
    v_major = int(data[maj_ind])
    v_minor = int(data[1 - maj_ind])
    byte_order = "<" if data[2] == b"I"[0] else ">"
    if v_major in (1, 2):
        return v_major, v_minor, byte_order

    raise ValueError(
        "Unknown subsystem data type, version {}, {}".format(v_major, v_minor)
    )


def read_subsystem(ssdata: BytesIO, **kwargs) -> Tuple[np.ndarray, str]:
    """Reads subsystem data"""

    ssStream = BytesIO(ssdata)

    mjv, mnv, byte_order = get_matfile_version(ssStream)
    if mjv != 1:
        raise NotImplementedError(f"Subsystem version {mjv}.{mnv} not supported")

    kwargs.pop("byte_order", None)
    kwargs.pop("variable_names", None)

    ssStream.seek(8)  # Skip subsystem header
    MR = MatFile5Reader(ssStream, byte_order=byte_order, **kwargs)
    MR.initialize_read()
    hdr, _ = MR.read_var_header()
    try:
        res = MR.read_var_array(hdr, process=True)
    except Exception as err:
        raise ValueError(f"Error reading subsystem data: {err}")

    return res, byte_order


def remove_unsupported_args(kwargs: Dict[str, Any]) -> None:
    # Remove unsupported arguments for scipy.io.loadmat
    kwargs.pop("simplify_cells", None)
    kwargs.pop("squeeze_me", None)
    kwargs.pop("struct_as_record", None)
    # uint16_codec = kwargs.pop("uint16_codec", sys.getdefaultencoding())
    # chars_as_strings = kwargs.pop("chars_as_strings", False)


def get_function_workspace(
    file_path: str, mdict=None, spmatrix=True, **kwargs
) -> bytes:
    matfile_dict = loadmat(file_path, mdict=mdict, spmatrix=spmatrix, **kwargs)
    ssdata = matfile_dict.pop("__function_workspace__", None)
    return matfile_dict, ssdata


def load_from_mat(
    file_path: str, mdict=None, raw_data: bool = False, *, spmatrix=True, **kwargs
) -> Dict[str, Any]:
    """Loads variables from MAT-file"""

    remove_unsupported_args(kwargs)

    matfile_dict, ssdata = get_function_workspace(file_path, mdict, spmatrix, **kwargs)
    if ssdata is None:
        # No subsystem data in file
        if mdict is not None:
            mdict.update(matfile_dict)
            return mdict
        return matfile_dict

    ss_array, byte_order = read_subsystem(ssdata, **kwargs)
    subsystem = SubsystemReader(ss_array, byte_order, raw_data)

    for var, data in matfile_dict.items():
        if not isinstance(data, np.ndarray):
            continue
        if data.dtype != OPAQUE_DTYPE:
            continue

        type_system = data[0]["_TypeSystem"]
        if type_system != "MCOS":
            warnings.warn(
                f"Unknown type system {type_system} for variable {var}. Skipping.",
                UserWarning,
            )
            continue

        metadata = data[0]["_Metadata"]
        matfile_dict[var] = subsystem.read_mcos_object(metadata)

    if mdict is not None:
        mdict.update(matfile_dict)
    else:
        mdict = matfile_dict

    return mdict
