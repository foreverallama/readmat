from typing import Any, List, Optional, Tuple

import numpy as np

CLASS_DTYPE = [
    ("__class__", "O"),
    ("__properties__", "O"),
    ("__handles__", "O"),
    ("__default_properties__", "O"),
    ("__s3__", "O"),
    ("__s2__", "O"),
]


class FileWrapper:
    def __init__(
        self, ssdata: np.ndarray, byte_order: str, raw_data: bool = False
    ) -> None:
        self.ssdata = ssdata
        self.byte_order = "<u4" if byte_order == "<" else ">u4"
        self.raw_data = raw_data
        if not self.check_subsystem_integrity():
            raise ValueError("Unknown format of subsystem data")
        self.names = self.get_field_names()

    def check_subsystem_integrity(self) -> bool:
        """Checks the integrity of the subsystem data"""
        toc_flag = np.frombuffer(
            self.ssdata[0, 0][0:4].tobytes(), dtype=self.byte_order
        )[0]
        if toc_flag != 4:
            raise ValueError("Unknown flag in FileWrapper table of contents")

        return True

    def check_object_reference(self, res: Any) -> bool:
        """Checks if the field content is a reference to another object"""
        # * Need to study condition with more examples

        if not isinstance(res, np.ndarray):
            return False
        if res.dtype != np.uint32:
            return False
        if res.shape[0] < 6:
            return False

        ref_value = res[0, 0]
        if ref_value != 0xDD000000:
            return False

        ndims = res[1, 0]
        if ndims <= 1:
            return False

        dims = res[2 : 2 + ndims, 0]
        total_objs = np.prod(dims)
        if total_objs <= 0:
            return False

        object_ids = res[2 + ndims : 2 + ndims + total_objs, 0]
        if np.any(object_ids <= 0):
            return False

        if object_ids.size + ndims + 3 != res.shape[0]:
            return False

        return True

    def get_object_dependencies(self, object_id: int) -> Tuple[int, int, int, int]:
        """Extracts object dependency IDs for a given object"""

        byte_offset = np.frombuffer(
            self.ssdata[0, 0][16:20].tobytes(), dtype=self.byte_order
        )[0]
        byte_offset = byte_offset + object_id * 24
        class_id, _, _, type1_id, type2_id, dep_id = np.frombuffer(
            self.ssdata[0, 0][byte_offset : byte_offset + 24].tobytes(),
            dtype=self.byte_order,
        )

        return class_id, type1_id, type2_id, dep_id

    def get_field_names(self) -> List[str]:
        """Extracts field and class names from the subsystem data"""

        byte_end = np.frombuffer(
            self.ssdata[0, 0][8:12].tobytes(), dtype=self.byte_order
        )[0]
        data = self.ssdata[0, 0][40:byte_end].tobytes()
        raw_strings = data.split(b"\x00")
        all_names = [s.decode("ascii") for s in raw_strings if s]
        return all_names

    def get_class_name(self, class_id: int) -> Tuple[Optional[str], str]:
        """Extracts class name and handle for a given object"""

        byte_offset = np.frombuffer(
            self.ssdata[0, 0][8:12].tobytes(), dtype=self.byte_order
        )[0]
        byte_offset = byte_offset + class_id * 16

        handle_idx, class_idx, _, _ = np.frombuffer(
            self.ssdata[0, 0][byte_offset : byte_offset + 16].tobytes(),
            dtype=self.byte_order,
        )

        class_name = self.names[class_idx - 1]
        handle_name = self.names[handle_idx - 1] if handle_idx > 0 else None
        return handle_name, class_name

    def get_ids(self, id: int, byte_offset: int, nbytes: int) -> np.ndarray:
        """Extract nblocks and subblock contents for a given object"""

        # Get block corresponding to type ID
        while id > 0:
            nblocks = np.frombuffer(
                self.ssdata[0, 0][byte_offset : byte_offset + 4].tobytes(),
                dtype=self.byte_order,
            )[0]
            byte_offset = byte_offset + 4 + nblocks * nbytes
            if ((nblocks * nbytes) + 4) % 8 != 0:
                byte_offset += 4
            id -= 1

        # Get the number of blocks
        nblocks = np.frombuffer(
            self.ssdata[0, 0][byte_offset : byte_offset + 4].tobytes(),
            dtype=self.byte_order,
        )[0]

        byte_offset += 4

        ids = np.frombuffer(
            self.ssdata[0, 0][byte_offset : byte_offset + nblocks * nbytes].tobytes(),
            dtype=self.byte_order,
        )

        return ids.reshape((nblocks, nbytes // 4))

    def get_handle_class_instance(self, type2_id: int) -> Tuple[int, int]:
        """Reads handle class instance ID for a given object"""

        start, end = np.frombuffer(
            self.ssdata[0, 0][16:24].tobytes(), dtype=self.byte_order
        )
        blocks = np.frombuffer(
            self.ssdata[0, 0][start:end].tobytes(), dtype=self.byte_order
        ).reshape(-1, 6)

        for idx, block in enumerate(blocks):
            if block[4] == type2_id:
                class_id = block[0]
                object_id = idx
                return class_id, np.array([object_id])

        raise ValueError(f"Handle class instance not found for type2_id: {type2_id}")

    def process_res_array(self, arr: Any) -> Any:
        """Iteratively check if result is an object reference and extract data"""

        # Implemented considering deeply nested arrays like Cells, Structs in MATLAB
        # If the object reference is within a cell or struct field, this will process it

        # Very hacky workaround to detect object references - needs to be improved
        # Best case scenario is to update scipy.io to detect this when reading integer arrays
        if not isinstance(arr, np.ndarray):
            return arr

        # Handling structured arrays
        if arr.dtype.names:
            result = np.empty_like(arr)
            for name in arr.dtype.names:
                result[name] = np.vectorize(self.process_res_array, otypes=[object])(
                    arr[name]
                )
            return result

        # Handling object arrays
        if arr.dtype == np.dtype("object"):
            result = np.empty_like(arr)

            for i, item in enumerate(arr.flat):
                idx = np.unravel_index(i, arr.shape)
                result[idx] = self.process_res_array(item)

            return result

        if self.check_object_reference(arr):
            object_ids, class_id, dims = get_object_reference(arr)
            return self.read_object_arrays(object_ids, class_id, dims)

        return arr

    def extract_fields(self, type1_id: int, type2_id: int, dep_id: int) -> np.ndarray:
        """Extracts the properties for an object"""

        if type1_id == 0 and type2_id != 0:
            obj_type_id = type2_id
            byte_offset = np.frombuffer(
                self.ssdata[0, 0][20:24].tobytes(), dtype=self.byte_order
            )[0]
        elif type1_id != 0 and type2_id == 0:
            obj_type_id = type1_id
            byte_offset = np.frombuffer(
                self.ssdata[0, 0][12:16].tobytes(), dtype=self.byte_order
            )[0]
        else:
            raise ValueError("Could not determine object type")

        field_ids = self.get_ids(obj_type_id, byte_offset, nbytes=12)
        field_names = [self.names[field_id - 1] for field_id in field_ids[:, 0]]
        field_dtype = [(name, object) for name in field_names]
        # Adding Handles
        handle_array = self.extract_handles(dep_id)
        if handle_array is not None:
            # Will be good to add handle name directly over here
            for idx, _ in enumerate(handle_array):
                field_dtype.append((f"__handle_{idx + 1}__", object))

        obj_props = np.empty((1, 1), dtype=field_dtype)

        for i, (field_type, field_value) in enumerate(field_ids[:, 1:]):
            if field_type == 1:
                res = self.ssdata[2 + int(field_value), 0]
                res = self.process_res_array(res)
                obj_props[0, 0][i] = res
            elif field_type == 2:
                obj_props[0, 0][i] = np.array(field_value, dtype=np.bool_)
            else:
                raise ValueError(f"Unknown field type: {field_type}")

        # Include Handle Values
        if handle_array is not None:
            for idx, handle in enumerate(handle_array):
                obj_props[0, 0][f"__handle_{idx + 1}__"] = handle

        return obj_props[0, 0]

    def extract_handles(self, dep_id: int) -> Optional[np.ndarray]:
        """Extracts the handle instances for an object"""

        # Get block corresponding to dep_id
        byte_offset = np.frombuffer(
            self.ssdata[0, 0][24:28].tobytes(), dtype=self.byte_order
        )[0]
        handle_type2_ids = self.get_ids(dep_id, byte_offset, nbytes=4)[:, 0]
        if handle_type2_ids.size == 0:
            return None

        handle_array = np.empty(handle_type2_ids.size, dtype=object)
        for i, handle_id in enumerate(handle_type2_ids):
            class_id, object_id = self.get_handle_class_instance(handle_id)
            handle_array[i] = self.read_object_arrays(object_id, class_id, dims=[1, 1])

        return handle_array

    def read_object_arrays(
        self, object_ids: np.ndarray, class_id: int, dims: List[int]
    ) -> np.ndarray:
        """Reads an object array for a given variable"""

        props_list = []
        for object_id in object_ids:
            _, type1_id, type2_id, dep_id = self.get_object_dependencies(object_id)
            obj_props = self.extract_fields(type1_id, type2_id, dep_id)
            # offsets[6] and offsets[7] are not used
            # Their purpose is unknown at the moment

            props_list.append(obj_props)

        obj_props = np.array(props_list).reshape(dims)

        obj_default_props = self.ssdata[-1, 0][class_id, 0]
        # Pulling default properties directly from the 1 x 1 struct array
        # Handles empty struct for default properties as well
        obj_default_props = (
            obj_default_props[0, 0]
            if obj_default_props.shape[1] > 0
            else obj_default_props[0]
        )

        if self.raw_data:
            # TODO
            # obj_props = convert_to_object(obj_props, obj_default_props)
            pass

        handle_name, class_name = self.get_class_name(class_id)
        if handle_name is not None:
            class_name = f"{handle_name}.{class_name}"

        # Remaining unknown class properties
        u1 = self.ssdata[-3, 0][class_id, 0]
        u2 = self.ssdata[-2, 0][class_id, 0]

        result = {
            "__class__": class_name,
            "__properties__": obj_props,
            "__default_properties__": obj_default_props,
            "__s3__": u1,
            "__s2__": u2,
        }

        return result


def get_object_reference(metadata: np.ndarray) -> Tuple[int, int, List[int]]:
    """Extracts object ID from the data array"""
    ref = metadata[0, 0]
    if ref != 0xDD000000:
        raise ValueError("Invalid object reference. Expected 0xDD000000. Got {ref}")

    ndims = metadata[1, 0]
    dims = metadata[2 : 2 + ndims, 0]
    if len(dims) != ndims:
        raise ValueError("Invalid dimensions. Expected {ndims}. Got {dims}")

    total_objs = np.prod(np.array(dims))
    object_ids = metadata[2 + ndims : 2 + ndims + total_objs, 0]
    class_id = metadata[-1, 0]

    return object_ids, class_id, dims
