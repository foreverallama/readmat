import os
from scipy.io import loadmat
from io import BytesIO
import struct
from scipy.io.matlab._mio5 import MatFile5Reader
from loadmat.src.class_parser import *


class SubsystemReader:

    def __init__(self, ssdata, byte_order=None, raw_data=False):
        self.ssdata = ssdata
        self.cell_pos = []
        self.offsets = []
        self.names = []
        self.raw_data = raw_data
        self.byte_order = byte_order
        if not byte_order:
            self.read_byte_order()

    def read_byte_order(self):
        self.ssdata.seek(2)
        data = self.ssdata.read(2)
        self.byte_order = "<" if data == b"IM" else ">"

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

        return res

    def read_mat_data(self, mat_data):
        """Read the data from the mat file."""
        byte_stream = BytesIO(mat_data)
        MR = MatFile5Reader(byte_stream)
        res = self.read_miMATRIX(MR)

        return res

    def extract_data(self, object):
        """Extract field contents for each object"""

        # Metadata for Type 1 objects are stored in offsets[1]
        # Type 2 objects in offsets[3]
        if object["type1_id"] != 0 and object["type2_id"] == 0:
            self.ssdata.seek(self.offsets[1])
            obj_dep_id = object["type1_id"]
        elif object["type1_id"] == 0 and object["type2_id"] != 0:
            self.ssdata.seek(self.offsets[3])
            obj_dep_id = object["type2_id"]

        self.ssdata.seek(8, 1)  # Discard first 8 bytes
        # Metadata is ordered by object ID
        # Find the correct metadata block for object ID
        while obj_dep_id - 1 > 0:
            data = self.ssdata.read(4)
            nblocks = struct.unpack(
                self.byte_order + "I", data
            )  # first integer gives number of subblocks
            nbytes = nblocks * 12  # each subblock is 12 bytes long
            nbytes = nbytes + (nbytes + 4) % 8  # padding to 8 byte boundary
            self.ssdata.seek(nbytes, 1)
            obj_dep_id -= 1

        # Read field contents for the given object ID
        data = self.ssdata.read(4)
        nfields = struct.unpack(self.byte_order + "I", data)[0]
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

        mat_obj = obj_dict
        # Wraps object in classes based on Matlab Class
        if not self.raw_data:
            mat_obj = self.convert_to_object(obj_dict, object["__class_name__"])

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
        class_names = []
        self.ssdata.seek(self.offsets[0])
        self.ssdata.seek(16, 1)  # Discard first val
        while self.ssdata.tell() < self.offsets[1]:
            data = self.ssdata.read(16)
            _, class_index, _, _ = struct.unpack(self.byte_order + "4I", data)
            class_names.append(self.names[class_index - 1])

        # Connecting class_ids to object_ids
        objects = {}
        self.ssdata.seek(self.offsets[2])
        self.ssdata.seek(24, 1)  # Discard first val
        while self.ssdata.tell() < self.offsets[3]:
            data = self.ssdata.read(24)
            class_id, _, _, type1_id, type2_id, object_id = struct.unpack(
                self.byte_order + "6I", data
            )
            objects[object_id] = {
                "class_id": class_id,
                "__class_name__": class_names[class_id - 1],
                "type1_id": type1_id,
                "type2_id": type2_id,
            }

        # Extract Data from Fields:
        for object in objects.keys():
            res = self.extract_data(objects[object])
            objects[object]["__fields__"] = res

        # Delete metadata
        for object in objects.keys():
            del objects[object]["class_id"]
            del objects[object]["type1_id"]
            del objects[object]["type2_id"]

        return objects

    def convert_to_object(self, obj_dict, class_name):
        """Converts the dictionary to a specific object based on the class name."""
        if class_name == "datetime":
            obj = MatDateTime(obj_dict)

        elif class_name == "duration":
            obj = MatDuration(obj_dict)

        elif class_name == "string":
            obj = parse_string(
                obj_dict,
                "any" if "any" in obj_dict else None,
                byte_order=self.byte_order,
            )

        else:
            print("Class not supported yet")
            obj = obj_dict

        return obj
    
def read_subsystem_data(file_path):
    """Reads subsystem data from file path and returns list of objects by their object IDs"""
    mdict = loadmat(file_path)
    data_reference = mdict["None"]
    var_name = data_reference["s0"][0].decode("utf-8")
    object_id = data_reference["arr"][0][4][0]

    ssdata = BytesIO(mdict["__function_workspace__"])
    SR = SubsystemReader(ssdata, raw_data=False)
    obj_dict = SR.parse_subsystem()
    obj_dict[var_name] = obj_dict.pop(object_id)
    return obj_dict