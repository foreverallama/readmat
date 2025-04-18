import numpy as np

from .class_parser import convert_to_object


class SubsystemReader:
    def __init__(self, ss_array, byte_order, raw_data=False):
        self.ssdata = ss_array
        self.byte_order = "<u4" if byte_order == "<" else ">u4"
        self.raw_data = raw_data
        self.fwrap_metadata = None
        self.fwrap_fields = None
        self.fwrap_defaults = None
        self.mcos_names = None
        self.init_fields()

    def init_fields(self):
        if "MCOS" in self.ssdata.dtype.names:
            fwrap_data = self.ssdata[0, 0]["MCOS"][0]["_Metadata"]
            self.fwrap_metadata = fwrap_data[0, 0][:, 0]
            toc_flag = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=0
            )[0]
            if toc_flag <= 1 or toc_flag > 4:
                raise ValueError("Incompatible FileWrapper version")
            if toc_flag == 2 or toc_flag == 3:
                # Not sure
                fwrap_version_offsets = 6
            elif toc_flag == 4:
                fwrap_version_offsets = 8

            self.fwrap_vals = fwrap_data[2:-3, 0]
            self.fwrap_defaults = fwrap_data[-3:, 0]
            self.mcos_names = self.get_field_names(fwrap_version_offsets)

    def get_field_names(self, num_offsets):
        """Extracts field and class names from the subsystem data"""

        byte_end = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=8
        )[0]
        byte_start = 8 + num_offsets * 4
        data = self.fwrap_metadata[byte_start:byte_end].tobytes()
        raw_strings = data.split(b"\x00")
        all_names = [s.decode("ascii") for s in raw_strings if s]
        return all_names

    def get_object_dependencies(self, object_id):
        """Extracts object dependency IDs for a given object"""

        byte_offset = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=16
        )[0]
        byte_offset = byte_offset + object_id * 24
        class_id, _, _, type1_id, type2_id, dep_id = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=6, offset=byte_offset
        )

        return class_id, type1_id, type2_id, dep_id

    def get_class_name(self, class_id):
        """Extracts class name and handle for a given object"""

        byte_offset = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=8
        )[0]
        byte_offset = byte_offset + class_id * 16

        handle_idx, class_idx, _, _ = np.frombuffer(
            self.fwrap_metadata,
            dtype=self.byte_order,
            count=4,
            offset=byte_offset,
        )

        class_name = self.mcos_names[class_idx - 1]
        handle_name = self.mcos_names[handle_idx - 1] if handle_idx > 0 else None
        return handle_name, class_name

    def get_ids(self, id, byte_offset, nbytes):
        """Extract nblocks and subblock contents for a given object"""

        # Get block corresponding to type ID
        while id > 0:
            nblocks = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=byte_offset
            )[0]
            byte_offset = byte_offset + 4 + nblocks * nbytes
            if ((nblocks * nbytes) + 4) % 8 != 0:
                byte_offset += 4
            id -= 1

        # Get the number of blocks
        nblocks = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=byte_offset
        )[0]

        byte_offset += 4
        ids = np.frombuffer(
            self.fwrap_metadata,
            dtype=self.byte_order,
            count=nblocks * nbytes // 4,
            offset=byte_offset,
        )

        return ids.reshape((nblocks, nbytes // 4))

    def get_handle_class_instance(self, type2_id):
        """Reads handle class instance ID for a given object"""

        start, end = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=2, offset=16
        )
        blocks = np.frombuffer(
            self.fwrap_metadata[start:end], dtype=self.byte_order
        ).reshape(-1, 6)

        for idx, block in enumerate(blocks):
            if block[4] == type2_id:
                class_id = block[0]
                object_id = idx
                return class_id, np.array([object_id])

        raise ValueError(f"Handle class instance not found for type2_id: {type2_id}")

    def extract_handles(self, dep_id):
        """Extracts the handle instances for an object"""

        # Get block corresponding to dep_id
        byte_offset = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=24
        )[0]
        handle_type2_ids = self.get_ids(dep_id, byte_offset, nbytes=4)[:, 0]
        if handle_type2_ids.size == 0:
            return None

        handles = {}
        for i, handle_id in enumerate(handle_type2_ids):
            class_id, object_id = self.get_handle_class_instance(handle_id)
            handles[f"_Handle_{i + 1}"] = self.read_object_arrays(
                object_id, class_id, dims=[1, 1]
            )
        return handles

    def find_object_reference(self, arr, path=()):
        if isinstance(arr, np.ndarray):
            if arr.dtype == object:
                # Iterate through cell arrays
                for idx in np.ndindex(arr.shape):
                    cell_item = arr[idx]
                    if check_object_reference(cell_item):
                        arr[idx] = self.read_mcos_object(cell_item)
                    else:
                        self.find_object_reference(cell_item, path + (idx,))
                    # Path to keep track of the current index
            elif arr.dtype.names:
                # Struct array
                for idx in np.ndindex(arr.shape):
                    for name in arr.dtype.names:
                        field_val = arr[idx][name]
                        if check_object_reference(field_val):
                            arr[idx][name] = self.read_mcos_object(field_val)
                        else:
                            self.find_object_reference(field_val, path + (idx, name))
            elif check_object_reference(arr):
                return self.read_mcos_object(arr)

        return arr

    def extract_fields(self, type1_id, type2_id, dep_id):
        """Extracts the properties for an object"""

        if type1_id == 0 and type2_id != 0:
            obj_type_id = type2_id
            byte_offset = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=20
            )[0]
        elif type1_id != 0 and type2_id == 0:
            obj_type_id = type1_id
            byte_offset = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=12
            )[0]
        else:
            raise ValueError("Could not determine object type")

        obj_props = {}
        field_ids = self.get_ids(obj_type_id, byte_offset, nbytes=12)
        for field_idx, field_type, field_value in field_ids:
            if field_type == 1:
                # field_content = self.find_object_reference(self.fwrap_vals[field_value])
                field_content = self.fwrap_vals[field_value]
                obj_props[self.mcos_names[field_idx - 1]] = field_content
            elif field_type == 2:
                obj_props[self.mcos_names[field_idx - 1]] = np.array(
                    field_value, dtype=np.bool_
                )
            else:
                raise ValueError(f"Unknown field type: {field_type}")

        # Include Handle Values
        handles = self.extract_handles(dep_id)
        if handles is not None:
            obj_props.update(handles)
        return obj_props

    def read_object_arrays(self, object_ids, class_id, dims):
        """Reads an object array for a given variable"""

        props_list = []
        for object_id in object_ids:
            _, type1_id, type2_id, dep_id = self.get_object_dependencies(object_id)
            obj_props = self.extract_fields(type1_id, type2_id, dep_id)
            props_list.append(obj_props)
        obj_props = np.array(props_list).reshape(dims)

        obj_default_props = self.fwrap_defaults[2][class_id, 0]
        if obj_default_props.size != 0:
            for name in obj_default_props.dtype.names:
                default_val = obj_default_props[name][0, 0]
                for idx in np.ndindex(obj_props.shape):
                    if name not in obj_props[idx]:
                        obj_props[idx][name] = default_val

        handle_name, class_name = self.get_class_name(class_id)
        if handle_name is not None:
            class_name = f"{handle_name}.{class_name}"

        # Converts some common MATLAB objects to Python objects
        if not self.raw_data:
            obj_props = convert_to_object(obj_props, class_name, self.byte_order)

        # Remaining unknown class properties
        _u1 = self.fwrap_defaults[0][class_id, 0]
        _u2 = self.fwrap_defaults[1][class_id, 0]

        result = {
            "_Class": class_name,
            "_Props": obj_props,
        }
        return result

    def read_mcos_enumeration(self, metadata):
        """Reads enumeration object from the metadata"""

        ref = metadata[0]["EnumerationInstanceTag"]
        if ref != 0xDD000000:
            return metadata

        class_idx = metadata[0]["ClassName"].item()
        builtin_class_index = metadata[0]["BuiltinClassName"].item()
        value_name_idx = metadata[0]["ValueNames"]

        class_name = self.mcos_names[class_idx - 1]
        if builtin_class_index != 0:
            builtin_class_name = self.mcos_names[builtin_class_index - 1]
        else:
            builtin_class_name = None

        value_idx = metadata[0]["ValueIndices"]
        value_names = [
            self.mcos_names[val - 1] for val in value_name_idx.ravel()
        ]  # Array is N x 1 shape
        value_names = np.array(value_names).reshape(value_idx.shape)

        enum_array = []
        mmdata = metadata[0]["Values"]  # Array is N x 1 shape
        if mmdata.size == 0:
            enum_array = np.array([])
        else:
            mmdata_map = mmdata[value_idx]
            for val in np.nditer(mmdata_map, flags=["refs_ok"], op_flags=["readonly"]):
                obj_array = self.read_normal_mcos(val.item())
                enum_array.append(obj_array)
            enum_array = np.array(enum_array).reshape(value_idx.shape)

        metadata[0]["ValueNames"] = value_names
        metadata[0]["Values"] = enum_array
        metadata[0]["ClassName"] = class_name
        metadata[0]["BuiltinClassName"] = builtin_class_name
        return metadata

    def read_normal_mcos(self, metadata):
        """Reads normal MCOS object from the metadata"""
        if not check_object_reference(metadata.ravel()):
            return metadata

        ndims = metadata[1, 0]
        dims = metadata[2 : 2 + ndims, 0]
        total_objs = np.prod(np.array(dims))
        object_ids = metadata[2 + ndims : 2 + ndims + total_objs, 0]
        class_id = metadata[-1, 0]
        return self.read_object_arrays(object_ids, class_id, dims)

    def read_mcos_object(self, metadata):
        if metadata.dtype.names is not None:
            if "EnumerationInstanceTag" in metadata.dtype.names:
                return self.read_mcos_enumeration(metadata.ravel())
            else:
                raise TypeError("Unknown metadata type {metadata.dtype}")

        elif metadata.dtype == np.uint32:
            return self.read_normal_mcos(metadata)

        return metadata


def check_object_reference(metadata):
    """Extracts object ID from the data array"""
    # Update to check for enumeration instances
    if not isinstance(metadata, np.ndarray) or not isinstance(metadata, np.uint32):
        return False
    if metadata.size < 6:
        return False
    if len(metadata.shape) < 2 or metadata.shape[1] != 1:
        return False

    ref = metadata[0]
    if ref != 0xDD000000:
        return False

    ndims = metadata[1]
    if ndims <= 1:
        return False

    dims = metadata[2 : 2 + ndims]
    total_objs = np.prod(np.array(dims))
    if total_objs <= 0:
        return False

    object_ids = metadata[2 + ndims : 2 + ndims + total_objs]
    if np.any(object_ids <= 0):
        return False
    if object_ids.size + ndims + 3 != metadata.shape[0]:
        return False

    class_id = metadata[-1]
    if class_id <= 0:
        return False
    return True
