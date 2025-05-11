"""MATLAB MAT-file version 7.3 (HDF5) reader."""

import h5py
import numpy as np
from scipy.io.matlab._mio_utils import (  # pylint: disable=no-name-in-module
    chars_to_strings,
)
from scipy.sparse import coo_matrix, issparse


class MatRead7:
    """Reads MAT-file version 7.3 (HDF5) files."""

    def __init__(self, file_stream, raw_data=False, add_table_attrs=False, chars_as_strings=True):
        """Initializes the MatRead7 object with the given file path."""
        self.h5stream = file_stream
        self.raw_data = raw_data
        self.add_table_attrs = add_table_attrs
        self.chars_as_strings = chars_as_strings

    def read_char(self, obj, is_empty=0):
        """Decodes MATLAB char arrays from the v7.3 MAT-file."""

        decode_type = obj.attrs.get("MATLAB_int_decode", None)
        raw = obj[()].T

        if is_empty:
            return np.empty(shape=raw, dtype=np.str_)

        if decode_type == 2:
            codec = "utf-16"
        else:
            raise NotImplementedError(
                f"MATLAB_int_decode {decode_type} not supported. Only 2 (utf-16) is supported."
            )

        decoded_arr = np.array(list(raw.tobytes().decode(codec))).reshape(raw.shape)
        if self.chars_as_strings:
            return chars_to_strings(decoded_arr)
        return decoded_arr

    def is_struct_matrix(self, hdf5_group):
        """
        Get struct array shape
        Scalar structs are stored directly as members of a group (can be nested)
        Struct arrays are stored as datasets of HDF5 references
        """
        for key in hdf5_group:
            obj = hdf5_group[key]
            if isinstance(obj, h5py.Group):
                return False
            if isinstance(obj, h5py.Dataset):
                class_name = obj.attrs.get("MATLAB_class", None)
                if class_name is not None:
                    return False
            else:
                # Any unexpected case?
                raise ValueError(f"Unexpected object type: {type(obj)}")
        return True

    def read_struct(self, obj, is_empty=0):
        """Reads MATLAB struct arrays from the v7.3 MAT-file."""

        if is_empty:
            # scipy.io.loadmat compatible
            return np.array([None], dtype=object).reshape(obj[()])

        fields = list(obj.keys())
        field_order = obj.attrs.get("MATLAB_fields", None)
        if field_order is not None:
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

    def read_h5_data(self, obj):
        """Reads data from the HDF5 object."""
        #* Remaining: Sparse, Object, Function, Opaque
        matlab_class = obj.attrs.get("MATLAB_class", None)
        is_empty = obj.attrs.get("MATLAB_empty", 0)

        if matlab_class == b"char":
            arr = self.read_char(obj, is_empty)
        elif matlab_class == b"logical":
            arr = obj[()].T.astype(np.bool_)
        elif matlab_class == b"struct":
            arr = self.read_struct(obj, is_empty)
        elif matlab_class == b"cell":
            arr = self.read_cell(obj, is_empty)
        else:
            #? int_decode attribute, is it useful?
            if is_empty:
                arr = np.empty(shape=obj[()], dtype=obj[()].dtype)
            else:
                arr = obj[()].T

        return arr

    def get_variables(self,
                    variable_names=None
                    ):
        """Reads variables from the HDF5 file."""
        if isinstance(variable_names, str):
            variable_names = [variable_names]
        elif variable_names is not None:
            variable_names = list(variable_names)

        mdict = {}
        mdict['__globals__'] = []

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

        hdict = {}
        hdict['__header__'] = hdr[0:116].decode('utf-8').strip(' \t\n\000')
        hdict['__version__'] = f"{v_major}.{v_minor}"
    return hdict

def read_matfile7(file_path,
                  raw_data=False,
                    add_table_attrs=False,
                    spmatrix=True,
                    _byte_order=None,
                    _mat_dtype=False,
                    chars_as_strings=True,
                    _verify_compressed_data_integrity=True,
                    variable_names=None):
    """Reads MAT-file version 7.3 (HDF5) files."""

    matfile_dict = read_file_header(file_path)
    f = h5py.File(file_path, "r")
    mat_reader = MatRead7(f, raw_data, add_table_attrs, chars_as_strings)
    try:
        mdict = mat_reader.get_variables(variable_names)
    finally:
        print('Closing file')
        f.close()

    if spmatrix:
        for name, var in list(matfile_dict.items()):
            if issparse(var):
                matfile_dict[name] = coo_matrix(var)

    matfile_dict.update(mdict)
    return matfile_dict
