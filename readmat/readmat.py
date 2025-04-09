import struct
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE

from .class_parser import convert_to_object


class SubsystemReader:
    def __init__(self, ssdata: BytesIO, raw_data: bool = False) -> None:
        self.ssdata: BytesIO = ssdata
        self._cell_pos: List[int] = []
        self.names: List[str] = []
        self.class_names: List[Tuple[Any | None, Any]] = []
        self._unique_objects: List[Tuple[int, int, int, int]] = []
        self._offsets: List[int] = []
        self._default_fields_pos: List[int] = []
        self.raw_data: bool = raw_data
        self.byte_order: str = self._read_byte_order()

        self._initialize_subsystem()

    def _read_byte_order(self) -> str:
        """Reads subsystem byte order"""

        self.ssdata.seek(2)
        data = self.ssdata.read(2)
        byte_order = "<" if data == b"IM" else ">"
        return byte_order

    def _read_field_content_ids(self) -> None:
        """Gets field content byte markers"""

        data = self.ssdata.read(
            8
        )  # Reads the miMATRIX Header of mxOPAQUE_CLASS metadata
        _, nbytes = struct.unpack(self.byte_order + "II", data)
        endPos = self.ssdata.tell() + nbytes

        self.ssdata.seek(40, 1)  # Discard variable headers
        while self.ssdata.tell() < endPos:
            self._cell_pos.append(self.ssdata.tell())
            data = self.ssdata.read(8)
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self.ssdata.seek(nbytes, 1)

    def _read_names_len(self) -> int:
        """Gets the length of the names"""

        data = self.ssdata.read(8)
        _, fc_len = struct.unpack(self.byte_order + "II", data)

        return fc_len

    def _read_region_offsets(self, cell1_start: int) -> List[int]:
        """Gets byte markers for region offsets"""

        data = self.ssdata.read(32)
        offsets_t = struct.unpack(self.byte_order + "8I", data)
        offsets = [offset + cell1_start for offset in offsets_t]

        return offsets

    def _read_class_names(self, fc_len: int, regionStart: int, regionEnd: int) -> None:
        """Parses Region 1 to extract class names"""

        # Get table of contents
        nbytes = regionStart - self.ssdata.tell()  # This block ends at offsets
        data = self.ssdata.read(nbytes)
        self.names = [s.decode("utf-8") for s in data.split(b"\x00") if s]

        # Extracting the class names
        self.ssdata.seek(regionStart)
        self.ssdata.seek(16, 1)  # Discard first val
        while self.ssdata.tell() < regionEnd:
            data = self.ssdata.read(16)
            handle_class_name_index, class_index, _, _ = struct.unpack(
                self.byte_order + "4I", data
            )
            handle_class_name = (
                self.names[handle_class_name_index - 1]
                if handle_class_name_index > 0
                else None
            )
            class_name = self.names[class_index - 1]
            self.class_names.append(
                (handle_class_name, class_name)
            )  # This list is ordered by class_id

    def _read_object_types(self, regionStart: int, regionEnd: int) -> None:
        """Parses Region 3 to extract object dependency IDs"""

        self.ssdata.seek(regionStart)
        self.ssdata.seek(24, 1)  # Discard first val which is all zeros

        while self.ssdata.tell() < regionEnd:
            data = self.ssdata.read(24)
            class_id, _, _, type1_id, type2_id, dep_id = struct.unpack(
                self.byte_order + "6I", data
            )
            self._unique_objects.append(
                (class_id, type1_id, type2_id, dep_id)
            )  # This list is ordered by object_id

    def _get_handle_pos(self, obj_dep_id: int) -> None:
        """Moves the file pointer to the handle object position"""

        self.ssdata.seek(self._offsets[4])  # Region 5
        self.ssdata.seek(8, 1)  # Discard first block

        while obj_dep_id - 1 > 0:
            # first integer gives number of handle objects
            data = self.ssdata.read(4)
            nhandles = struct.unpack(self.byte_order + "I", data)[0]

            # each handle represented by 4 byte integer
            nbytes = nhandles * 4
            nbytes = nbytes + ((nbytes + 4) % 8)
            self.ssdata.seek(nbytes, 1)
            obj_dep_id -= 1

    def _get_default_field_pos(self) -> None:
        """Gets the byte markers for arrays containing default property values of an object"""

        self.ssdata.seek(self._cell_pos[-1])  # Last Cell
        self.ssdata.seek(8, 1)  # Reads the miMATRIX Header
        self.ssdata.seek(16, 1)  # Skip Array Flags

        data = self.ssdata.read(8)  # Reads dimensions flag of cell array
        _, ndims = struct.unpack(self.byte_order + "II", data)
        data = self.ssdata.read(ndims)
        dims = struct.unpack(self.byte_order + "I" * (ndims // 4), data)
        if ndims // 4 > 2 or dims[1] != 1:
            raise ValueError(
                "Invalid dimensions for default fields. Expected Nx1 array."
            )

        self.ssdata.seek(ndims % 8, 1)  # Padding to 8 byte boundary
        self.ssdata.seek(8, 1)  # Skip variable name

        for i in range(0, dims[0]):
            data = self.ssdata.read(8)  # Reads the miMATRIX Header
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self._default_fields_pos.append(
                self.ssdata.tell() - 8
            )  # Extract struct array pos
            self.ssdata.seek(nbytes, 1)

        self._default_fields_pos = self._default_fields_pos[
            1:
        ]  # First struct is ignored

    def _initialize_subsystem(self) -> None:
        """parses the subsystem data and and links different parts of metadata"""
        self.ssdata.seek(144)  # discard headers

        self._read_field_content_ids()

        # Parsing Cell 1
        self.ssdata.seek(self._cell_pos[0])
        self.ssdata.seek(8, 1)  # Discard miMATRIX Header
        self.ssdata.seek(48, 1)  # Discard Variable Header

        # Extracting metadata offset byte markers
        cell1_start = self.ssdata.tell()
        fc_len = self._read_names_len()
        self._offsets = self._read_region_offsets(cell1_start)

        self._read_class_names(
            fc_len, regionStart=self._offsets[0], regionEnd=self._offsets[1]
        )
        self._read_object_types(
            regionStart=self._offsets[2], regionEnd=self._offsets[3]
        )
        self._get_default_field_pos()

        return

    def get_object_dependencies(self, object_id: int) -> Tuple[int, int, int, int]:
        """Get the object dependencies for a given object ID"""

        return self._unique_objects[object_id - 1]

    def get_class_name(self, class_id: int) -> Tuple[Any | None, Any]:
        """Get the class name for a given class ID"""

        return self.class_names[class_id - 1]

    def check_object_reference(self, res: Any) -> bool:
        """Checks if the field content is a reference to another object"""
        if not isinstance(res, np.ndarray):
            return False

        if res.dtype != np.uint32:
            return False

        if res.shape[0] < 6:
            return False

        ref_value = res[0, 0]
        ndims = res[1, 0]
        shapes = res[2 : 2 + ndims, 0]

        if ref_value != 0xDD000000:
            return False

        if ndims <= 1 or len(shapes) != ndims:
            return False

        # # * Need to study condition with more examples
        # if np.count_nonzero(shapes != 1) > 1:  # At most 1 dimension can have size > 1
        #     return False

        return True

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
            object_id = arr[-2, 0].item()
            ndims = arr[1, 0].item()
            dims = arr[2 : 2 + ndims, 0]
            return self.read_object_arrays(object_id, dims)

        return arr

    def read_miMATRIX(self, MR: MatFile5Reader) -> Any:
        """Wrapper function around the get_variables() of scipy.io.matlab MatFile5Reader class."""

        MR.byte_order = self.byte_order
        MR.mat_stream.seek(0)
        MR.initialize_read()
        while not MR.end_of_stream():
            hdr, _ = MR.read_var_header()
            try:
                res = MR.read_var_array(hdr, process=True)
            except Exception as e:
                err = f"Read error: {e}"
                print(err)

            res = self.process_res_array(res)

        return res

    def read_mat_data(self, mat_data: bytes) -> Any:
        """Read the data from the mat file. Wrapper around scipy.io.matlab MatFile5Reader class."""

        byte_stream = BytesIO(mat_data)
        MR = MatFile5Reader(byte_stream)
        res = self.read_miMATRIX(MR)
        return res

    def get_num_fields(self, type1_id: int, type2_id: int) -> Optional[int]:
        """Extract the number of fields for the object"""

        # Metadata for Type 1 objects are stored in offsets[1]
        # Type 2 objects in offsets[3]
        if type1_id != 0 and type2_id == 0:
            self.ssdata.seek(self._offsets[1])
            obj_type_id = type1_id
        elif type1_id == 0 and type2_id != 0:
            self.ssdata.seek(self._offsets[3])
            obj_type_id = type2_id
        else:
            obj_type_id = 0  # No flag

        if obj_type_id == 0:
            return None

        self.ssdata.seek(8, 1)  # Discard first 8 bytes
        # Metadata is ordered by object type ID
        # Find the correct metadata block for object type ID

        while obj_type_id - 1 > 0:
            # first integer gives number of subblocks
            data = self.ssdata.read(4)
            nblocks = struct.unpack(self.byte_order + "I", data)[0]

            # each subblock is 12 bytes long
            nbytes = nblocks * 12
            nbytes = nbytes + (nbytes + 4) % 8  # padding to 8 byte boundary
            self.ssdata.seek(nbytes, 1)
            obj_type_id -= 1

        data = self.ssdata.read(4)  # Read nfields
        nfields = struct.unpack(self.byte_order + "I", data)[0]

        return nfields

    def get_default_fields(self, class_id: int) -> Dict[str, Any]:
        """Extract the properties with default values for an object"""

        def_class_pos = self._default_fields_pos[class_id - 1]
        self.ssdata.seek(def_class_pos)
        data = self.ssdata.read(8)  # Read miMATRIX header
        _, nbytes = struct.unpack(self.byte_order + "II", data)
        self.ssdata.seek(-8, 1)
        mat_data = self.ssdata.read(nbytes + 8)  # Read the full cell contents
        obj_default_fields = self.read_mat_data(mat_data)
        # Wrap in dict
        if obj_default_fields.size == 0:
            return {}
        else:
            return {
                field: obj_default_fields[0, 0][field]
                for field in obj_default_fields.dtype.names
            }
            # Indexing by (0,0) since the struct array is expected to be 1x1 dimensions

    def extract_from_field(self, nfields: int, class_id: int) -> Dict[str, Any]:
        """Extracts contents of each field of an object"""

        curPos = self.ssdata.tell()
        obj_fields = self.get_default_fields(class_id)

        self.ssdata.seek(curPos)
        while nfields > 0:
            # Extract field name
            data = self.ssdata.read(12)
            field_index, field_type, field_value = struct.unpack(
                self.byte_order + "3I", data
            )
            field_name = self.names[field_index - 1]
            curPos = self.ssdata.tell()

            if field_type == 2:  # Logical Attribute
                obj_fields[field_name] = field_value
                nfields -= 1
                continue

            # Extract contents from field name
            self.ssdata.seek(
                self._cell_pos[field_value + 2]
            )  # adding two since array includes Cell 1 and Cell 2
            data = self.ssdata.read(8)
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self.ssdata.seek(-8, 1)
            mat_data = self.ssdata.read(nbytes + 8)  # Read the full cell contents
            obj_fields[field_name] = self.read_mat_data(mat_data)

            # Move to next field
            self.ssdata.seek(curPos)
            nfields -= 1

        return obj_fields

    def extract_fields(
        self, class_id: int, type1_id: int, type2_id: int
    ) -> Tuple[Dict[str, Any], Any, Any | None]:
        """Extracts the fields from the object"""

        nfields = (
            self.get_num_fields(type1_id, type2_id) or 0
        )  # If nfields is None, set to 0
        obj_fields = self.extract_from_field(nfields, class_id)
        handle_class_name, class_name = self.get_class_name(class_id)

        fields = obj_fields
        if not self.raw_data:
            fields = convert_to_object(obj_fields, class_name, self.byte_order)

        return fields, class_name, handle_class_name

    def extract_handles(self, obj_dep_id: int) -> Optional[Dict[str, Any]]:
        """Reads handle objects of a class"""

        self._get_handle_pos(obj_dep_id)

        data = self.ssdata.read(4)
        nhandles = struct.unpack(self.byte_order + "I", data)[0]
        if nhandles == 0:
            return None

        nbytes = nhandles * 4
        data = self.ssdata.read(nbytes)
        handle_type2_ids = struct.unpack(self.byte_order + "I" * nhandles, data)

        handle_dict = {}
        key_index = 1
        for handle_id in handle_type2_ids:
            obj_id = next(
                (
                    i + 1
                    for i, t in enumerate(self._unique_objects)
                    if t[2] == handle_id
                ),
                -1,
            )
            if obj_id == -1:
                raise ValueError(f"Object ID {handle_id} not found in handle_type1_ids")

            class_id, _, _, _ = self.get_object_dependencies(obj_id)
            handle_class_name, class_name = self.get_class_name(class_id)
            key_name = f"{handle_class_name}.{class_name}.{key_index}"
            handle_dict[key_name] = self.read_object_arrays(obj_id, dims=[1, 1])
            key_index += 1

        return handle_dict

    def read_nested_objects(self, object_id: int) -> Dict[str, Any]:
        """Reads nested objects for a given object
        For e.g. if the property of an object is another object"""

        class_id, type1_id, type2_id, dep_id = self.get_object_dependencies(object_id)
        obj, class_name, handle_class_name = self.extract_fields(
            class_id, type1_id, type2_id
        )
        obj_handles = self.extract_handles(dep_id)

        res = {"__class_name__": class_name, "__fields__": obj}

        if handle_class_name is not None:
            res["__handle_class__"] = handle_class_name
        if obj_handles is not None:
            res["__fields__"].update(obj_handles)

        return res

    def read_object_arrays(self, object_id: int, dims: List[int]) -> np.ndarray:
        """Reads an object array for a given variable"""

        obj_array = []
        total_objects_in_array = np.prod(np.array(dims))

        for i in range(object_id - total_objects_in_array + 1, object_id + 1):
            _, _, _, dep_id = self.get_object_dependencies(object_id)
            ndeps = dep_id - object_id
            res = self.read_nested_objects(object_id=i)
            obj_array.append(res)
            i = i + ndeps

        obj_array = np.reshape(obj_array, dims)
        return obj_array


def get_object_metadata(data: np.ndarray) -> Tuple[List[int], int]:
    """Extracts object ID from the data array"""

    # Extract the object ID from the metadata
    metadata = data[0]["object_metadata"]
    if metadata.dtype == np.uint32:
        ref = metadata[0, 0]
        if ref != 0xDD000000:
            raise ValueError("Invalid object reference")
        ndims = metadata[1, 0]
        dims = metadata[2 : 2 + ndims, 0]
        object_id = metadata[-2, 0]

    elif metadata.dtype.fields is not None:
        if "EnumerationInstanceTag" in metadata.dtype.fields:
            raise TypeError("EnumerationInstances is not supported currently")
        else:
            raise TypeError(
                "Unknown metadata format. Please raise issue with developers"
            )

    else:
        raise TypeError("Unknown metadata format. Please raise issue with developers")

    return dims, object_id


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

        dims, object_id = get_object_metadata(data)

        # Read all objects in array
        obj_array = SR.read_object_arrays(object_id, dims)
        mdict[var] = obj_array

    return mdict


def read_subsystem_data_legacy(
    file_path: str, raw_data: bool = False
) -> Dict[str, Any]:
    """Reads subsystem data from file path and returns list of objects by their object IDs"""
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
