"""Reads MCOS subsystem data from MAT files"""

import warnings

import numpy as np

from matio.convert import convert_to_object, mat_to_enum


class SubsystemReader:
    """Extracts object properties from the subsystem data
    Currently only supports MCOS objects
    """

    def __init__(self, byte_order, raw_data=False, add_table_attrs=False):
        self.byte_order = (
            "<u4" if byte_order == "<" else ">u4"
        )  # Could potentially be int32
        self.raw_data = raw_data
        self.add_table_attrs = add_table_attrs
        self.fwrap_metadata = None
        self.fwrap_vals = None
        self.fwrap_defaults = None
        self.mcos_names = None

    def init_fields_v7(self, ssdata):
        """Fetches metadata and field contents from the subsystem data
        Currently only supports MCOS objects
        Attributes:
            1. fwrap_metadata: Metadata for MCOS objects
            2. fwrap_vals: Numpy array of properties of MCOS objects
            3. fwrap_defaults: Numpy array of default properties of MCOS classes
            4. mcos_names: List of field and class names of all MCOS objects in file
        """
        if "MCOS" in ssdata.dtype.names:
            fwrap_data = ssdata[0, 0]["MCOS"][0]["_Metadata"]
            self.fwrap_metadata = fwrap_data[0, 0][:, 0]
            toc_flag = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=0
            )[0]
            if toc_flag in (2, 3):
                # Not sure
                fwrap_version_offsets = 6
            elif toc_flag == 4:
                fwrap_version_offsets = 8
            else:
                raise ValueError("Incompatible FileWrapper version")

            self.fwrap_vals = fwrap_data[2:-3, 0]
            self.fwrap_defaults = fwrap_data[-3:, 0]
            self.mcos_names = self.get_field_names(fwrap_version_offsets)

    def init_fields_v73(self, ssdata):
        """Fetches metadata and field contents from the subsystem data
        Different format from aove due to scipy.io.loadmat compatibility
        """

        if "MCOS" in ssdata.dtype.names:
            self.fwrap_metadata = ssdata[0, 0]["MCOS"][0,0]
            toc_flag = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=0
            )[0]
            if toc_flag in (2, 3):
                # Not sure
                fwrap_version_offsets = 6
            elif toc_flag == 4:
                fwrap_version_offsets = 8
            else:
                raise ValueError("Incompatible FileWrapper version")

            self.fwrap_vals = ssdata[0, 0]["MCOS"][2:-3,0]
            self.fwrap_defaults = ssdata[0, 0]["MCOS"][-3:,0]
            self.mcos_names = self.get_field_names(fwrap_version_offsets)

    def get_field_names(self, num_offsets):
        """Extracts field and class names from the subsystem data
        Names are stored as a list of null-terminated strings
        Inputs:
            1. num_offsets: Number of offsets in the metadata
            This is determined by FileWrapper version
        Returns:
            1. all_names: List of field and class names
        """
        byte_end = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=8
        )[0]
        byte_start = 8 + num_offsets * 4
        data = self.fwrap_metadata[byte_start:byte_end].tobytes()
        raw_strings = data.split(b"\x00")
        all_names = [s.decode("ascii") for s in raw_strings if s]
        return all_names

    def get_object_dependencies(self, object_id):
        """Extracts object dependency IDs for a given object
        Dependency IDs are stored in blocks of 24 bytes ordered by object ID
        Each block contains:
            1. Class ID
            2. Unknown flag
            3. Unknown flag
            4. Type1 ID
            5. Type2 ID
            6. Dependency ID

        Inputs:
            1. object_id: ID of the object
        Returns:
            (class_id, type1_id, type2_id, dep_id)
        """

        byte_offset = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=1, offset=16
        )[0]
        byte_offset = byte_offset + object_id * 24
        class_id, _, _, type1_id, type2_id, dep_id = np.frombuffer(
            self.fwrap_metadata, dtype=self.byte_order, count=6, offset=byte_offset
        )

        return class_id, type1_id, type2_id, dep_id

    def get_class_name(self, class_id):
        """Extracts class name and handle for a given object from its class ID
        Class IDs are stored in blocks of 16 bytes ordered by class ID
        Each block contains:
            1. Handle Name Index
            2. Class Name Index
            3. Unknown flag
            4. Unknown flag
        Inputs:
            1. class_id: ID of the class
        Returns:
            (handle_name, class_name)
        """

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

    def get_ids(self, m_id, byte_offset, nbytes):
        """Extract nblocks and subblock contents for a given object
        Helper method to parse metadata with the format:
            1. nsubblocks (4 bytes)
            2. subblock contents (nblocks * nbytes)

        Inputs:
            1. m_id: ID of the object
            2. byte_offset: Offset to start reading from
            3. nbytes: Number of bytes in each subblock
        Returns:
            1. ids: Numpy array of all subblock contents
        """

        # Get block corresponding to type ID
        while m_id > 0:
            nblocks = np.frombuffer(
                self.fwrap_metadata, dtype=self.byte_order, count=1, offset=byte_offset
            )[0]
            byte_offset = byte_offset + 4 + nblocks * nbytes
            if ((nblocks * nbytes) + 4) % 8 != 0:
                byte_offset += 4
            m_id -= 1

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
        """Reads handle class instance ID for a given object
        Searches for the object ID of the corresponding handle class from its type 2 ID
        Inputs:
            1. type2_id: ID of the handle instance
        Returns:
            1. class_id of the handle instance
            2. object_id of the handle instance
        """

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
        """Extracts the handle instances for an object
        Handle instances attached to an object are tagged by their type 2 IDs
        Objects with handle instances can be found by their dependency ID
        """

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
        """Recursively searches for object references in the data array
        and replaces them with the corresponding MCOS object.

        This is a hacky solution to find object arrays inside struct arrays or cell arrays.
        """

        if not isinstance(arr, np.ndarray):
            return arr

        if check_object_reference(arr):
            return self.read_mcos_object(arr)

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
            # Iterate through struct array
            if check_object_reference(arr):
                return self.read_mcos_object(arr)
            for idx in np.ndindex(arr.shape):
                for name in arr.dtype.names:
                    field_val = arr[idx][name]
                    if check_object_reference(field_val):
                        arr[idx][name] = self.read_mcos_object(field_val)
                    else:
                        self.find_object_reference(field_val, path + (idx, name))

        return arr

    def parse_field_types(self, field_type, field_value, type1_id, class_name):
        """Parses field types and values for an object"""

        if field_type == 0:
            val = self.mcos_names[field_value - 1]
        elif field_type == 1:
            if type1_id and class_name == "function_handle_object":
                # Special case to break circular reference in nested function handle
                val = self.fwrap_vals[field_value]
            else:
                val = self.find_object_reference(self.fwrap_vals[field_value])
        elif field_type == 2:
            val = field_value
        else:
            raise ValueError(f"Unknown field type: {field_type}")

        return val

    def extract_fields(self, object_id, class_name):
        """Extracts the properties for an object
        Inputs:
            (type1_id, type2_id, dep_id): Dependency IDs of the object
        Returns:
            1. obj_props: Dictionary of object properties keyed by property names
        """

        _, type1_id, type2_id, dep_id = self.get_object_dependencies(object_id)

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
            obj_props[self.mcos_names[field_idx - 1]] = self.parse_field_types(
                field_type, field_value, type1_id, class_name
            )
            # Sending type1_id and class_name to parse_field
            # for special case of function_handle_object

        # Include Handle Values
        handles = self.extract_handles(dep_id)
        if handles is not None:
            obj_props.update(handles)
        return obj_props

    def read_object_arrays(self, object_ids, class_id, dims):
        """Reads an object array for a given variable
        Inputs:
            1. object_ids: IDs of the objects
            2. class_id: ID of the class
            3. dims: Dimensions of the object array
        Returns:
            1. result: Dictionary representing the object array
            Dictionary contains:
                - _Class: Class name
                - _Props: Numpy array of object properties
        """

        # Attach class name to the object
        handle_name, class_name = self.get_class_name(class_id)
        if handle_name is not None:
            class_name = f"{handle_name}.{class_name}"

        if object_ids.size == 0:
            return {
                "_Class": class_name,
                "_Props": np.empty(dims, dtype=object),
            }

        if object_ids[0] == 0:
            # Deleted object
            return {
                "_Class": class_name,
            }

        props_list = []
        for object_id in object_ids:
            obj_props = self.extract_fields(object_id, class_name)
            props_list.append(obj_props)
        obj_props = np.array(props_list).reshape(dims)

        obj_default_props = self.fwrap_defaults[2][class_id, 0]
        obj_default_props = self.find_object_reference(obj_default_props)
        # Update object properties with any default values
        if obj_default_props.size != 0:
            for name in obj_default_props.dtype.names:
                default_val = obj_default_props[name][0, 0]
                for idx in np.ndindex(obj_props.shape):
                    if name not in obj_props[idx]:
                        obj_props[idx][name] = default_val

        # Converts some common MATLAB objects to Python objects
        result = convert_to_object(
            obj_props, class_name, self.byte_order, self.raw_data, self.add_table_attrs
        )

        # Remaining unknown class properties
        # _u1 = self.fwrap_defaults[0][class_id, 0]
        # _u2 = self.fwrap_defaults[1][class_id, 0]

        return result

    def read_mcos_enumeration(self, metadata):
        """Reads MCOS enumeration object from the metadata
        Inputs:
            metadata: Metadata for the enumeration object
        Returns:
            metadata: Metadata for the enumeration object
            If raw_data is False, returns the enumeration object
        """

        handle_name, class_name = self.get_class_name(
            metadata[0, 0]["ClassName"].item()
        )
        if handle_name is not None:
            class_name = f"{handle_name}.{class_name}"

        builtin_class_index = metadata[0, 0]["BuiltinClassName"].item()
        if builtin_class_index != 0:
            handle_name, builtin_class_name = self.get_class_name(builtin_class_index)
            if handle_name is not None:
                builtin_class_name = f"{handle_name}.{builtin_class_name}"
        else:
            builtin_class_name = None

        value_names = [
            self.mcos_names[val - 1] for val in metadata[0, 0]["ValueNames"].ravel()
        ]  # Array is N x 1 shape

        enum_vals = []
        value_idx = metadata[0, 0]["ValueIndices"]
        mmdata = metadata[0, 0]["Values"]  # Array is N x 1 shape
        if mmdata.size != 0:
            mmdata_map = mmdata[value_idx]
            for val in np.nditer(mmdata_map, flags=["refs_ok"], op_flags=["readonly"]):
                obj_array = self.read_normal_mcos(val.item())
                enum_vals.append(obj_array)

        if not self.raw_data:
            enum_array = mat_to_enum(
                enum_vals,
                value_names,
                class_name,
                value_idx.shape,
            )
            return enum_array

        metadata[0, 0]["BuiltinClassName"] = builtin_class_name
        metadata[0, 0]["ClassName"] = class_name
        metadata[0, 0]["ValueNames"] = np.array(value_names).reshape(
            value_idx.shape, order="F"
        )
        metadata[0, 0]["ValueIndices"] = value_idx
        metadata[0, 0]["Values"] = np.array(enum_vals).reshape(
            value_idx.shape, order="F"
        )

        return metadata

    def read_normal_mcos(self, metadata):
        """Reads normal MCOS object from the metadata"""

        ndims = metadata[1, 0]
        dims = metadata[2 : 2 + ndims, 0]
        if dims.size == 0:
            total_objs = np.uint64(0)
        else:
            total_objs = np.prod(dims)

        object_ids = metadata[2 + ndims : 2 + ndims + total_objs, 0]
        class_id = metadata[-1, 0]
        return self.read_object_arrays(object_ids, class_id, dims)

    def read_mcos_object(self, metadata, type_system="MCOS"):
        """Reads MCOS object based on OPAQUE_DTYPE CONTENTS"""
        if type_system != "MCOS":
            warnings.warn(
                f"Type system {type_system} is not supported.",
                UserWarning,
            )
            return metadata

        if metadata.dtype.names is not None:
            if "EnumerationInstanceTag" in metadata.dtype.names:
                return self.read_mcos_enumeration(metadata)

            warnings.warn(
                "Couldn't read MCOS object type, returning object metadata",
                UserWarning,
            )
            return metadata

        if metadata.dtype == np.uint32:
            return self.read_normal_mcos(metadata)

        return metadata


def check_object_reference(metadata):
    """Checks if the metadata is a valid object reference"""
    if not isinstance(metadata, np.ndarray):
        return False

    if metadata.dtype.names:
        if "EnumerationInstanceTag" in metadata.dtype.names:
            if (
                metadata[0, 0]["EnumerationInstanceTag"].dtype == np.uint32
                and metadata[0, 0]["EnumerationInstanceTag"].size == 1
                and metadata[0, 0]["EnumerationInstanceTag"] == 0xDD000000
            ):
                return True
        return False

    if not (
        metadata.dtype == np.uint32
        and metadata.ndim == 2
        and metadata.shape == (metadata.shape[0], 1)
        and metadata.size >= 3
    ):
        return False

    if metadata[0, 0] != 0xDD000000:
        return False

    return True
