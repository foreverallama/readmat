import os
from io import BytesIO
import struct
# from scipy.io.matlab._mio5 import MatFile5Reader
# from scipy.io.matlab._mio5_params import OPAQUE_DTYPE
from readmat.class_parser import *

class SubsystemReaderNew:
    def __init__(self, ssdata):
        self.ssdata = ssdata
        self.cell_pos = []
        self.names = []
        self.class_names = []
        self.unique_objects = []
        self.byte_order = self.read_byte_order()

        self.initialize_subsystem()

    def read_byte_order(self):
        """Reads subsystem byte order"""

        self.ssdata.seek(2)
        data = self.ssdata.read(2)
        byte_order = "<" if data == b"IM" else ">"
        return byte_order
    
    def read_field_content_ids(self):
        """Gets field content byte markers"""

        data = self.ssdata.read(8)
        _, nbytes = struct.unpack(self.byte_order + "II", data)
        endPos = self.ssdata.tell() + nbytes

        self.ssdata.seek(40, 1)
        self.cell_pos.append(self.ssdata.tell())
        while self.ssdata.tell() < endPos:
            data = self.ssdata.read(8)
            _, nbytes = struct.unpack(self.byte_order + "II", data)
            self.cell_pos.append(self.ssdata.tell() + nbytes) # This is ordered by field_content_id
            self.ssdata.seek(nbytes, 1)

    def read_names_len(self):
        """Gets the length of the names"""

        data = self.ssdata.read(8)
        _, fc_len = struct.unpack(self.byte_order + "II", data)
        
        return fc_len
    
    def read_region_offsets(self, cell1_start):
        """Gets byte markers for region offsets"""

        data = self.ssdata.read(32)
        offsets = struct.unpack(self.byte_order + "8I", data)
        offsets = [offset + cell1_start for offset in offsets]

        return offsets
    
    def read_class_names(self, fc_len, regionStart, regionEnd):
        """Parses Region 1"""

        # Get table of contents
        nbytes = regionStart - self.ssdata.tell()  # This block ends at offsets
        data = self.ssdata.read(nbytes)
        self.names = [s.decode("utf-8") for s in data.split(b"\x00") if s]

        # Extracting the class names
        self.ssdata.seek(regionStart)
        self.ssdata.seek(16, 1)  # Discard first val
        while self.ssdata.tell() < regionEnd:
            data = self.ssdata.read(16)
            _, class_index, _, _ = struct.unpack(self.byte_order + "4I", data)
            self.class_names.append(self.names[class_index - 1]) # This list is ordered by class_id

    def read_object_types(self, regionStart, regionEnd):
        """Parses Region 3"""

        self.ssdata.seek(regionStart)
        self.ssdata.seek(24, 1)  # Discard first val which is all zeros

        while self.ssdata.tell() < regionEnd:
            data = self.ssdata.read(24)
            class_id, _, _, type1_id, type2_id, dep_id = struct.unpack(
                self.byte_order + "6I", data
            )
            self.unique_objects.append((class_id, type1_id, type2_id, dep_id)) # This list is ordered by object_id

    def initialize_subsystem(self):
        """parses the subsystem data and and creates a link"""
        self.ssdata.seek(144)  # discard headers

        self.read_field_content_ids()

        # Parsing Cell 1
        self.ssdata.seek(self.cell_pos[0])
        self.ssdata.seek(8, 1)  # Discard miMATRIX Header
        self.ssdata.seek(48, 1)  # Discard Variable Header

        # Extracting metadata offset byte markers
        cell1_start = self.ssdata.tell()
        fc_len = self.read_names_len()
        offsets = self.read_region_offsets(cell1_start)

        self.read_class_names(fc_len, regionStart=offsets[0], regionEnd=offsets[1])
        self.read_object_types(regionStart=offsets[2], regionEnd=offsets[3])

        return 
    
    def get_object_dependencies(self, object_id):
        """Get the object dependencies for a given object ID"""
        
        return self.unique_objects[object_id - 1]