"""MATLAB MAT-file version 7.3 (HDF5) reader."""

import warnings

import h5py
import numpy as np
from scipy.io.matlab._mio5_params import MatlabObject
from scipy.io.matlab._mio_utils import (  # pylint: disable=no-name-in-module
    chars_to_strings,
)
from scipy.sparse import coo_matrix, csc_array, issparse

from matio.subsystem import SubsystemReader


class MatRead7:
    """Reads MAT-file version 7.3 (HDF5) files."""

    def __init__(self, file_stream, raw_data=False, add_table_attrs=False, chars_as_strings=True):
        """Initializes the MAT-file reader.
        Parameters
        ----------
            file_stream : h5py.File object
            raw_data : bool, optional
            add_table_attrs : bool, optional
            chars_as_strings : bool, optional
        """
        self.h5stream = file_stream
        self.subsystem = None
        self.raw_data = raw_data
        self.add_table_attrs = add_table_attrs
        self.chars_as_strings = chars_as_strings

    def initialize_v73_subsystem(self, byte_order, raw_data, add_table_attrs):
        """Initializes the subsystem for v7.3 MAT-files."""

        subsystem_arr = self.read_struct(self.h5stream["#subsystem#"])
        subsystem = SubsystemReader(byte_order, raw_data, add_table_attrs)
        subsystem.init_fields_v73(subsystem_arr)
        return subsystem

    def read_int(self, obj, is_empty=0):
        """Reads MATLAB integer arrays from the v7.3 MAT-file."""

        int_decode = obj.attrs.get("MATLAB_int_decode", None)
        if int_decode is not None:
            warnings.warn(
                f"MATLAB_int_decode {int_decode} is not supported. "
                "This may lead to unexpected behaviour.", UserWarning
            )

        if is_empty:
            return np.empty(shape=obj[()], dtype=obj[()].dtype)

        arr = obj[()]
        if arr.dtype.names:
            # complex number
            real = arr["real"]
            imag = arr["imag"]
            arr = np.empty(shape=arr.shape, dtype=np.complex128)
            arr.real = real
            arr.imag = imag

        return arr.T

    def read_char(self, obj, is_empty=0):
        """Decodes MATLAB char arrays from the v7.3 MAT-file."""

        decode_type = obj.attrs.get("MATLAB_int_decode", None)
        raw = obj[()].T

        if is_empty:
            return np.empty(shape=raw, dtype=np.str_)

        if decode_type == 2:
            codec = "utf-16"
        else:
            warnings.warn(
                f"MATLAB_int_decode {decode_type} not supported. "
                "This may lead to unexpected behaviour",
                UserWarning
            )
            codec = "utf-8"

        decoded_arr = np.array(list(raw.tobytes().decode(codec))).reshape(raw.shape)
        if self.chars_as_strings:
            return chars_to_strings(decoded_arr)
        return decoded_arr

    def is_struct_matrix(self, hdf5_group):
        """Check if the HDF5 struct group is a struct matrix or scalar"""

        # Scalar structs are stored directly as members of a group (can be nested)
        # Struct arrays are stored as datasets of HDF5 references
        for key in hdf5_group:
            obj = hdf5_group[key]
            if isinstance(obj, h5py.Group):
                return False

            if isinstance(obj, h5py.Dataset):
                class_name = obj.attrs.get("MATLAB_class", None)
                if class_name is not None:
                    return False

        return True

    def read_struct(self, obj, is_empty=0):
        """Reads MATLAB struct arrays from the v7.3 MAT-file."""

        if is_empty:
            return np.empty(shape=obj[()], dtype=object)

        fields = list(obj.keys())
        field_order = obj.attrs.get("MATLAB_fields", None)
        if field_order is not None:
            # For maximum compatibility with scipy.io
            fields = [''.join(x.astype(str)) for x in field_order]

        if self.is_struct_matrix(obj):
            is_scalar = False
            shape = next(iter(obj.values())).shape
        else:
            is_scalar = True
            shape = (1, 1)

        dt = [(name, object) for name in fields]
        arr = np.empty(shape=shape, dtype=dt)

        for field in obj:
            obj_field = obj[field]
            for idx in np.ndindex(arr.shape):
                if is_scalar:
                    arr[idx][field] = self.read_h5_data(obj_field)
                else:
                    arr[idx][field] = self.read_h5_data(self.h5stream[obj_field[idx]])
        return arr.T

    def read_cell(self, obj, is_empty=0):
        """Reads MATLAB cell arrays from the v7.3 MAT-file."""

        if is_empty:
            return np.empty(shape=obj[()], dtype=object)

        arr = np.empty(shape=obj.shape, dtype=object)
        for idx in np.ndindex(obj.shape):
            ref_data = self.h5stream[obj[idx]]
            arr[idx] = self.read_h5_data(ref_data)
        return arr.T

    def read_sparse(self, obj, nrows):
        """Reads MATLAB sparse arrays from the v7.3 MAT-file."""

        jc = obj['jc'][()]
        ncols = jc.size - 1

        if 'data' in obj:
            # Exists only if sparse matrix contains non-zero elements
            data = self.read_int(obj['data'])
            ir = obj['ir'][()]
        else:
            data = np.array([], dtype=np.float64)
            ir = np.array([], dtype=np.int32)

        return csc_array((data, ir, jc), shape=(nrows, ncols))

    def read_function_handle(self, obj, object_decode):
        """Reads MATLAB function handles from the v7.3 MAT-file."""

        # Uses object_decode = 1 probably

        if object_decode == 1:
            return self.read_struct(obj)

        raise NotImplementedError(
            f"Function handle object_decode {object_decode} not supported. Only 1 is supported."
        )

    def read_object(self, obj, class_name):
        """Reads mxOBJECT_CLASS variables from the v7.3 MAT-file."""

        class_name = class_name.decode("utf-8")
        fields = self.read_struct(obj)

        return MatlabObject(fields, class_name)

    def get_type_system(self, class_name):
        """Gets the type system for the given class name."""

        # Possibly, MATLAB decodes internally based on class name
        # This function is just guess work as of now
        class_name = class_name.decode("utf-8")
        if class_name.startswith("java.") or class_name.startswith("com."):
            type_system = "java"
        elif class_name.startswith("COM."):
            type_system = "handle"
        else:
            type_system = "MCOS"

        return type_system

    def read_opaque(self, obj, object_decode, is_empty=0):
        """Reads MATLAB opaque objects from the v7.3 MAT-file."""

        class_name = obj.attrs.get("MATLAB_class", None)
        if class_name == b"FileWrapper__":
            return self.read_cell(obj)

        if object_decode == 2:
            # object_decode is a flag indicating how to decode objects
            # Object Decode = 1 -> Function Handle (possibly)
            # Object Decode = 2 -> mxOBJECT_CLASS
            # Object Decode = 3 -> mxOPAQUE_CLASS
            return self.read_object(obj, class_name)

        if is_empty:
            return np.empty(shape=obj[()], dtype=object)

        if self.subsystem is None:
            raise ValueError("Subsystem not initialized. Cannot read opaque objects.")

        type_system = self.get_type_system(class_name)

        # Check Enumeration Instances
        fields = obj.attrs.get("MATLAB_fields", None)
        if fields is not None:
            fields = [''.join(x.astype(str)) for x in fields]

            if "EnumerationInstanceTag" in fields:
                metadata = self.read_struct(obj)
                if metadata[0, 0]["EnumerationInstanceTag"] != 0xDD000000:
                    return metadata
            else:
                metadata = obj[()].T
        else:
            metadata = obj[()].T
        return self.subsystem.read_mcos_object(metadata, type_system)

    def read_h5_data(self, obj):
        """Reads data from the HDF5 object."""

        matlab_class = obj.attrs.get("MATLAB_class", None)
        is_empty = obj.attrs.get("MATLAB_empty", 0)
        object_decode = obj.attrs.get("MATLAB_object_decode", -1)
        matlab_sparse = obj.attrs.get("MATLAB_sparse", -1)

        if matlab_sparse >= 0:
            arr = self.read_sparse(obj, matlab_sparse)
        elif matlab_class == b"char":
            arr = self.read_char(obj, is_empty)
        elif matlab_class == b"logical":
            arr = obj[()].T.astype(np.bool_)
        elif matlab_class in (
            b"int8", b"uint8", b"int16", b"uint16",
            b"int32", b"uint32", b"int64", b"uint64",
            b"single", b"double"
        ):
            arr = self.read_int(obj, is_empty)
        elif matlab_class == b"struct":
            arr = self.read_struct(obj, is_empty)
        elif matlab_class == b"cell":
            arr = self.read_cell(obj, is_empty)
        elif matlab_class == b"function_handle":
            arr = self.read_function_handle(obj, object_decode)
        elif matlab_class == b"canonical empty" and is_empty:
            arr = np.empty(shape=(0, 0), dtype=object)
        elif object_decode >= 0:
            arr = self.read_opaque(obj, object_decode, is_empty)
        else:
            raise NotImplementedError(
                f"MATLAB class {matlab_class} not supported", UserWarning)

        return arr

    def get_variables(self, variable_names, byte_order, raw_data, add_table_attrs):
        """Reads variables from the HDF5 file."""
        if isinstance(variable_names, str):
            variable_names = [variable_names]
        elif variable_names is not None:
            variable_names = list(variable_names)

        mdict = {}
        mdict['__globals__'] = []

        if '#subsystem#' in self.h5stream:
            self.subsystem = self.initialize_v73_subsystem(byte_order, raw_data, add_table_attrs)

        for var in self.h5stream:
            obj = self.h5stream[var]
            if var in ('#refs#', '#subsystem#'):
                continue
            if variable_names is not None and var not in variable_names:
                continue
            try:
                data = self.read_h5_data(obj)
            except Exception as err:
                raise ValueError(f"Error reading variable {var}: {err}") from err
            mdict[var] = data
            is_global = obj.attrs.get("MATLAB_global", 0)
            if is_global:
                mdict['__globals__'].append(var)
            if variable_names is not None:
                variable_names.remove(var)
                if len(variable_names) == 0:
                    break
        return mdict

def read_file_header(file_path):
    """Reads the file header of the MAT-file."""
    with open(file_path, "rb") as f:
        f.seek(0)
        hdr = f.read(128)
        v_major = hdr[125] if hdr[126] == b'I'[0] else hdr[124]
        v_minor = hdr[124] if hdr[126] == b'I'[0] else hdr[125]
        byte_order = "<" if hdr[126] == b'I'[0] else ">"

        hdict = {}
        hdict['__header__'] = hdr[0:116].decode('utf-8').strip(' \t\n\000')
        hdict['__version__'] = f"{v_major}.{v_minor}"
    return hdict, byte_order

def read_matfile7(file_path,
                  raw_data=False,
                  add_table_attrs=False,
                  spmatrix=True,
                  byte_order=None, # pylint: disable=unused-argument
                  mat_dtype=False, # pylint: disable=unused-argument
                  chars_as_strings=True,
                  verify_compressed_data_integrity=True, # pylint: disable=unused-argument
                  variable_names=None):
    """Reads MAT-file version 7.3 (HDF5) files.
    Parameters
    ----------
        file_path : str
            Path to the MAT-file.
        raw_data : bool, optional
            If True, returns raw data for MATLAB object instances. Default is False.
        add_table_attrs : bool, optional
            If True, adds table attributes to Pandas DataFrames. Default is False.
        spmatrix : bool, optional
            If True, converts sparse matrices to COO format. Default is True.
        chars_as_strings : bool, optional
            If True, converts character arrays to strings. Default is True.
        variable_names : list of str or str, optional
            Names of variables to read from the MAT-file. Default is None (reads all variables)."""

    matfile_dict, byte_order = read_file_header(file_path)
    f = h5py.File(file_path, "r")
    mat_reader = MatRead7(f, raw_data, add_table_attrs, chars_as_strings)
    try:
        mdict = mat_reader.get_variables(variable_names, byte_order, raw_data, add_table_attrs)
    finally:
        f.close()

    if spmatrix:
        for name, var in list(matfile_dict.items()):
            if issparse(var):
                matfile_dict[name] = coo_matrix(var)

    matfile_dict.update(mdict)
    return matfile_dict
