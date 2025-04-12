import sys
import warnings
from io import BytesIO
from typing import Any, Dict, Tuple

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from .subsystem import FileWrapper, get_object_reference


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


def read_subsystem(ssStream: BytesIO, **kwargs) -> Tuple[np.ndarray, str]:
    """Reads subsystem data"""

    mjv, mnv, byte_order = get_matfile_version(ssStream)
    if mjv != 1:
        raise NotImplementedError(f"Subsystem version {mjv}.{mnv} not supported")

    ssStream.seek(8)  # Skip subsystem header
    kwargs.pop(
        "byte_order", None
    )  # Remove byte order from kwargs, obtained from subsystem header
    kwargs.pop(
        "variable_names", None
    )  # Remove variable names from kwargs, not needed for reading subsystem data

    MR = MatFile5Reader(ssStream, byte_order=byte_order, **kwargs)
    MR.initialize_read()
    hdr, _ = MR.read_var_header()
    try:
        res = MR.read_var_array(hdr, process=True)
    except Exception as err:
        raise ValueError(f"Error reading subsystem data: {err}")

    return res, byte_order


def load_enumeration_object(metadata: np.ndarray, fwrap: FileWrapper) -> np.ndarray:
    """Extracts enumeration instance from subsystem using object metadata"""

    ref = metadata[0, 0]["EnumerationInstanceTag"]
    if ref != 0xDD000000:
        raise ValueError("Invalid object reference. Expected 0xDD000000. Got {ref}")

    class_idx = metadata[0, 0]["ClassName"].item()
    class_name = fwrap.names[class_idx - 1]
    builtin_class_index = metadata[0, 0]["BuiltinClassName"].item()
    if builtin_class_index != 0:
        builtin_class_name = fwrap.names[builtin_class_index - 1]
    else:
        builtin_class_name = None

    value_idx = metadata[0, 0]["ValueIndices"]
    value_name_idx = metadata[0, 0]["ValueNames"]
    value_names = [fwrap.names[val - 1] for val in value_name_idx.flat]
    value_names = np.array(value_names).reshape(value_idx.shape)

    enum_array = []
    for val in value_idx.flat:
        mmdata = metadata[0, 0]["Values"]
        if mmdata.size == 0:
            obj_array = np.array([])
        else:
            obj_array = load_MCOS_object(mmdata[val, 0], fwrap)
        enum_array.append(obj_array)

    enum_array = np.array(enum_array).reshape(value_idx.shape)

    metadata[0, 0]["ValueNames"] = value_names
    metadata[0, 0]["Values"] = enum_array
    metadata[0, 0]["ClassName"] = class_name
    metadata[0, 0]["BuiltinClassName"] = builtin_class_name

    return metadata


def load_MCOS_object(metadata: np.ndarray, fwrap: FileWrapper) -> np.ndarray:
    object_ids, class_id, dims = get_object_reference(metadata)
    obj_array = fwrap.read_object_arrays(object_ids, class_id, dims)
    # if obj_array.size == 0:
    # return np.array([])
    return obj_array


def check_object_type(mm: np.ndarray) -> int:
    """Extracts object ID from the data array"""

    if mm.dtype == np.uint32:
        obj_type = 1

    elif mm.dtype.fields is not None:
        if "EnumerationInstanceTag" in mm.dtype.fields:
            obj_type = 2
        else:
            raise TypeError("Unknown metadata type {mm.dtype}")

    elif mm.dtype == np.uint8:
        obj_type = 3  # Possible Java object

    else:
        raise TypeError("Unknown metadata format {mm}")

    return obj_type


def load_from_mat(
    file_path: str, mdict=None, raw_data: bool = False, *, spmatrix=True, **kwargs
) -> Dict[str, Any]:
    """Loads variables from MAT-file"""

    # Remove unsupported arguments for scipy.io.loadmat
    kwargs.pop("simplify_cells", None)
    kwargs.pop("squeeze_me", None)
    kwargs.pop("struct_as_record", None)

    matfile_dict = loadmat(file_path, mdict=mdict, spmatrix=spmatrix, **kwargs)
    ssdata = matfile_dict.pop("__function_workspace__", None)
    if ssdata is None:
        print("No subsystem data found in the file.")

        if mdict is not None:
            mdict.update(matfile_dict)
            return mdict
        return matfile_dict

    ssStream = BytesIO(ssdata)
    res, byte_order = read_subsystem(ssStream, **kwargs)
    ss_fields = res[0, 0].dtype.fields
    uint16_codec = kwargs.pop("uint16_codec", sys.getdefaultencoding())
    chars_as_strings = kwargs.pop("chars_as_strings", False)
    if "MCOS" in ss_fields:
        fwrap = FileWrapper(
            res[0, 0]["MCOS"][()]["__object_metadata__"],
            byte_order,
            raw_data,
            chars_as_strings,
            uint16_codec,
        )

    if "java" in ss_fields:
        warnings.warn(
            "Java object found in the file. These are not supported yet.", UserWarning
        )

    for var, data in matfile_dict.items():
        # Skip mdict headers
        if not isinstance(data, np.ndarray):
            continue

        # Skip non opaque data
        if data.dtype != OPAQUE_DTYPE:
            continue

        metadata = data[()]["__object_metadata__"]
        obj_type = check_object_type(metadata)
        if obj_type == 1:
            obj_array = load_MCOS_object(metadata, fwrap)
        elif obj_type == 2:
            obj_array = load_enumeration_object(metadata, fwrap)
        elif obj_type == 3:
            # obj_array = load_java_object(metadata, res[0,0]['Java'], byte_order, raw_data)
            continue
        else:
            warnings.warn(
                f"Unknown object type {obj_type} for variable {var}. Skipping.",
                UserWarning,
            )
            continue

        matfile_dict[var] = obj_array

    if spmatrix:
        from scipy.sparse import coo_matrix, issparse

        for name, var in list(matfile_dict.items()):
            if issparse(var):
                # This would not recognize sparse matrices within struct/cell/object arrays
                # Ideally, pass this bool to process_res_array
                matfile_dict[name] = coo_matrix(var)

    if mdict is not None:
        mdict.update(matfile_dict)
    else:
        mdict = matfile_dict

    return mdict
