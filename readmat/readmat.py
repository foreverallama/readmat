from io import BytesIO
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from .subsystem import SubsystemReader


def get_object_reference(metadata: np.ndarray) -> Tuple[int, List[int]]:
    """Extracts object ID from the data array"""
    ref = metadata[0, 0]
    if ref != 0xDD000000:
        raise ValueError("Invalid object reference. Expected 0xDD000000. Got {ref}")
    ndims = metadata[1, 0]
    dims = metadata[2 : 2 + ndims, 0]
    object_id = metadata[-2, 0]

    return object_id, dims


def load_normal_object(metadata: np.ndarray, SR: SubsystemReader) -> np.ndarray:
    """Extracts objects from subsystem using object metadata"""
    object_id, dims = get_object_reference(metadata)
    obj_array = SR.read_object_arrays(object_id, dims)
    if obj_array.size == 0:
        return np.array([])
    return obj_array


def load_enumeration_object(
    metadata: np.ndarray, SR: SubsystemReader
) -> Dict[str, Any]:
    """Extracts enumeration instance from subsystem using object metadata"""
    ref = metadata[0, 0]["EnumerationInstanceTag"]
    if ref != 0xDD000000:
        raise ValueError("Invalid object reference. Expected 0xDD000000. Got {ref}")

    class_index = metadata[0, 0]["ClassName"].item()
    _, class_name = SR.get_class_name(class_index)
    builtin_class_index = metadata[0, 0]["BuiltinClassName"].item()
    if builtin_class_index != 0:
        _, builtin_class_name = SR.get_class_name(builtin_class_index)
    else:
        builtin_class_name = None

    value_name_idx = metadata[0, 0]["ValueNames"]
    value_names = [SR.names[val - 1] for val in value_name_idx.flat]

    # Extract the enumeration values
    value_idx = metadata[0, 0]["ValueIndices"]

    enum_array = []
    for val in value_idx.flat:
        mmdata = metadata[0, 0]["Values"]
        if mmdata.size == 0:
            obj_array = np.array([])
        else:
            obj_array = load_normal_object(mmdata[val, 0], SR)

        obj_dict = {value_names[val]: obj_array}
        enum_array.append(obj_dict)

    enum_array = np.array(enum_array).reshape(value_idx.shape)
    enum_dict = {
        "__class_name__": class_name,
        "__builtin_class_name__": (
            builtin_class_name if builtin_class_name is not None else ""
        ),
        "__fields__": enum_array,
    }

    return enum_dict


def check_object_type(metadata: np.ndarray) -> int:
    """Extracts object ID from the data array"""

    if metadata.dtype == np.uint32:
        obj_type = 1

    elif metadata.dtype.fields is not None:
        if "EnumerationInstanceTag" in metadata.dtype.fields:
            obj_type = 2
        else:
            raise TypeError("Unknown metadata format {metadata.dtype}")

    else:
        raise TypeError("Unknown metadata format {metadata}")

    return obj_type


def load_from_mat(file_path: str, raw_data: bool = False) -> Dict[str, Any]:
    """Reads data from file path and returns all data"""

    mdict = loadmat(file_path)
    ssdata = mdict.pop("__function_workspace__", None)
    if ssdata is None:
        print("No subsystem data found in the file.")
        return mdict

    ssdata = BytesIO(ssdata)
    SR = SubsystemReader(ssdata, raw_data)

    for var, data in mdict.items():
        if not isinstance(data, np.ndarray):
            continue

        if data.dtype != OPAQUE_DTYPE:
            continue

        metadata = data[0]["object_metadata"]
        obj_type = check_object_type(metadata)
        if obj_type == 1:
            obj_array = load_normal_object(metadata, SR)
        elif obj_type == 2:
            obj_array = load_enumeration_object(metadata, SR)

        mdict[var] = obj_array

    return mdict


def read_subsystem_data_legacy(
    file_path: str, raw_data: bool = False
) -> Dict[str, Any]:
    """Reads subsystem data from file path and returns list of objects by their object IDs
    Legacy implementation based on stable scipy.io.loadmat release
    """
    mdict = loadmat(file_path)
    data_reference = mdict["None"]
    var_name = data_reference["s0"][0].decode("utf-8")
    object_id = data_reference["arr"][0][4][0]
    ndims = data_reference["arr"][0][1][0]
    dims = [data_reference["arr"][0][2 + i][0] for i in range(ndims)]

    ssdata = BytesIO(mdict["__function_workspace__"])
    SR = SubsystemReader(ssdata, raw_data)
    obj_dict = SR.read_object_arrays(object_id, dims)
    obj_dict[var_name] = obj_dict.pop(object_id)
    return obj_dict
