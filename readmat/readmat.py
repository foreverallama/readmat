import os
from scipy.io import loadmat
from io import BytesIO
import struct
from scipy.io.matlab._mio5 import MatFile5Reader
from scipy.io.matlab._mio5_params import OPAQUE_DTYPE
from readmat.class_parser import *


class SubsystemReader:

    def __init__(self, ssdata, raw_data=False):
        self.ssdata = ssdata
        self.cell_pos = []
        self.offsets = []
        self.names = []
        self.unique_objects = []
        self.raw_data = raw_data
        self.class_names = []
        self.processed_ids = []
        self.byte_order = self.read_byte_order()

    def read_byte_order(self):
        self.ssdata.seek(2)
        data = self.ssdata.read(2)
        byte_order = "<" if data == b"IM" else ">"
        return byte_order

    def read_miMATRIX(self, MR):
        """Wrapper function around the get_variables() of the MatFile5Reader class."""
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
    
    def process_res_array(self, arr):
        """Iteratively check if result is an object reference and extract data"""
        
        # Implemented considering deeply nested arrays like Cells, Structs in MATLAB
        # If the object reference is within a cell or struct field, this will process it
        
        # Very hacky workaround to detect object references - needs to be improved
        # Best case scenario is to update scipy.io to detect this when reading integer arrays
        if not isinstance(arr, np.ndarray):
            return arr
        
        if arr.dtype == np.dtype('object'):
            result = np.empty_like(arr)
            
            for i, item in enumerate(arr.flat):
                idx = np.unravel_index(i, arr.shape)
                result[idx] = self.process_res_array(item)
            
            return result
        else:
            if self.check_object_reference(arr):
                object_id = arr[-2, 0].item()
                self.processed_ids.append(object_id)
                return self.extract_data(object_id)
            
        return arr
        
    def read_mat_data(self, mat_data):
        """Read the data from the mat file."""
        byte_stream = BytesIO(mat_data)
        MR = MatFile5Reader(byte_stream)
        res = self.read_miMATRIX(MR)
        return res

    def check_object_reference(self, res):
        """Checks if the field content is an object reference"""
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

        # * Need to study condition with more examples
        if np.count_nonzero(shapes != 1) > 1:  # At most 1 dimension can have size > 1
            return False

        return True

    def extract_data(self, object_id):
        """Extract field contents for each object"""

        class_id, type1_id, type2_id = self.unique_objects[object_id - 1]

        # Metadata for Type 1 objects are stored in offsets[1]
        # Type 2 objects in offsets[3]
        if type1_id != 0 and type2_id == 0:
            self.ssdata.seek(self.offsets[1])
            obj_dep_id = type1_id
        elif type1_id == 0 and type2_id != 0:
            self.ssdata.seek(self.offsets[3])
            obj_dep_id = type2_id
        else:
            obj_dep_id = 0  # No flag

        self.ssdata.seek(8, 1)  # Discard first 8 bytes
        # Metadata is ordered by object ID
        # Find the correct metadata block for object ID
        while obj_dep_id - 1 > 0:
            data = self.ssdata.read(4)
            nblocks = struct.unpack(self.byte_order + "I", data)[
                0
            ]  # first integer gives number of subblocks
            nbytes = nblocks * 12  # each subblock is 12 bytes long
            nbytes = nbytes + (nbytes + 4) % 8  # padding to 8 byte boundary
            self.ssdata.seek(nbytes, 1)
            obj_dep_id -= 1

        # Read field contents for the given object ID
        data = self.ssdata.read(4)
        nfields = struct.unpack(self.byte_order + "I", data)[0]
        object = {"__class_name__": self.class_names[class_id - 1]}
        obj_dict = {}
        while nfields > 0:
            # Extract field name
            data = self.ssdata.read(12)
            field_index, _, field_content_index = struct.unpack(
                self.byte_order + "3I", data
            )
            field_name = self.names[field_index - 1]
            curPos = self.ssdata.tell()

            # Extract contents from field name
            self.ssdata.seek(
                self.cell_pos[field_content_index + 2]
            )  # adding two since array includes Cell 1 and Cell 2
            data = self.ssdata.read(8)
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self.ssdata.seek(-8, 1)
            mat_data = self.ssdata.read(nbytes + 8)  # Read the full cell content
            obj_dict[field_name] = self.read_mat_data(mat_data)

            # Move to next field
            self.ssdata.seek(curPos)
            nfields -= 1

        object["__fields__"] = obj_dict

        # Wraps object in classes based on Matlab Class
        mat_obj = object
        if not self.raw_data:
            mat_obj = self.convert_to_object(object)

        return mat_obj

    def parse_subsystem(self):
        """parses the subsystem data and returns a dictionary of objects with their fields and field contents"""
        self.ssdata.seek(144)  # discard headers

        # extract byte marker of field content cells
        data = self.ssdata.read(8)
        _, nbytes = struct.unpack(self.byte_order + "II", data)
        endPos = self.ssdata.tell() + nbytes

        self.ssdata.seek(40, 1)
        self.cell_pos.append(self.ssdata.tell())
        while self.ssdata.tell() < endPos:
            data = self.ssdata.read(8)
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self.cell_pos.append(self.ssdata.tell() + nbytes)
            self.ssdata.seek(nbytes, 1)

        # Parsing Cell 1
        self.ssdata.seek(self.cell_pos[0])
        self.ssdata.seek(8, 1)  # Discard miMATRIX Header
        self.ssdata.seek(48, 1)  # Discard Variable Header

        # Extracting number of field and class names
        cell1_start = self.ssdata.tell()
        data = self.ssdata.read(8)
        _, fc_len = struct.unpack(self.byte_order + "II", data)

        # Extracting metadata offset byte markers
        data = self.ssdata.read(32)
        self.offsets = struct.unpack(self.byte_order + "8I", data)
        self.offsets = [offset + cell1_start for offset in self.offsets]

        ## Extracting field and class names
        nbytes = self.offsets[0] - self.ssdata.tell()  # This block ends at offsets[0]
        data = self.ssdata.read(nbytes)
        self.names = [s.decode("utf-8") for s in data.split(b"\x00") if s]

        # Extracting the class names
        self.ssdata.seek(self.offsets[0])
        self.ssdata.seek(16, 1)  # Discard first val
        while self.ssdata.tell() < self.offsets[1]:
            data = self.ssdata.read(16)
            _, class_index, _, _ = struct.unpack(self.byte_order + "4I", data)
            self.class_names.append(self.names[class_index - 1])

        # Connecting class_ids to object_ids
        self.ssdata.seek(self.offsets[2])
        self.ssdata.seek(24, 1)  # Discard first val

        while self.ssdata.tell() < self.offsets[3]:
            data = self.ssdata.read(24)
            class_id, _, _, type1_id, type2_id, _ = struct.unpack(
                self.byte_order + "6I", data
            )
            self.unique_objects.append((class_id, type1_id, type2_id))

        # Extract Data from Fields:
        objects = {}
        for object_id in range(1, len(self.unique_objects) + 1):
            if object_id in self.processed_ids:
                continue

            res = self.extract_data(object_id)
            objects[object_id] = res
            self.processed_ids.append(object_id)

        return objects

    def convert_to_object(self, obj_dict):
        """Converts the dictionary to a specific object based on the class name."""

        class_name = obj_dict["__class_name__"]
        fields = obj_dict["__fields__"]

        if class_name == "datetime":
            obj = MatDateTime(fields)

        elif class_name == "duration":
            obj = MatDuration(fields)

        elif class_name == "string":
            obj = parse_string(
                fields,
                "any" if "any" in fields else None,
                byte_order=self.byte_order,
            )

        else:
            print("Class not supported yet")
            obj = obj_dict

        return obj


def read_subsystem_data_legacy(file_path, raw_data=False):
    """Reads subsystem data from file path and returns list of objects by their object IDs"""
    mdict = loadmat(file_path)
    data_reference = mdict["None"]
    var_name = data_reference["s0"][0].decode("utf-8")
    object_id = data_reference["arr"][0][4][0]

    ssdata = BytesIO(mdict["__function_workspace__"])
    SR = SubsystemReader(ssdata, raw_data)
    obj_dict = SR.parse_subsystem()
    obj_dict[var_name] = obj_dict.pop(object_id)
    return obj_dict


def merge_dicts(mdict, obj_dict):
    """Merges two dictionaries."""
    for key, value in mdict.items():
        if not isinstance(value, np.ndarray):
            continue
        if value.dtype == OPAQUE_DTYPE:
            object_id = value["object_id"].item()
            if object_id in obj_dict:
                mdict[key] = obj_dict[object_id]

    return mdict


def read_subsystem_data(file_path, raw_data=False):
    """Reads subsystem data from file path and returns list of objects by their object IDs"""
    mdict = loadmat(file_path)
    ssdata = BytesIO(mdict["__function_workspace__"])
    SR = SubsystemReader(ssdata, raw_data)
    obj_dict = SR.parse_subsystem()
    mdict1 = merge_dicts(mdict, obj_dict)  # Merge the dictionaries in place
    return mdict1
