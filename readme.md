# ReadMat Module

The `readmat` module provides tools for reading and parsing `.mat` files, particularly for extracting contents from user-defined objects or MATLAB datatypes such as `datetime`, `table` and `string`. It uses a wrapper built around `scipy.io` to extract raw subsystem data from MAT-files, which is then parsed and interpreted to extract object data. It includes utilities for reading MATLAB objects like `datetime` and `duration` both as raw data or their respective Python objects.

 Currently supported MATLAB objects are:

- `string`
- `datetime`
- `duration`
- `table`
- `timetable`
- User-defined objects

## Usage

Clone and install using pip:

```bash
git clone https://github.com/foreverallama/readmat.git
pip install .
# OR
pip install git+https://github.com/foreverallama/readmat.git
```

### `readmat.load_from_mat(file_path, raw_data=False, mdict=None, *, spmatrix=True, **kwargs)`

#### Parameters:

- **`file_path`**: `str`
  Full path to the MAT-file.

- **`raw_data`**: `bool`, *optional*
  If `False`, returns object data as raw MATLAB structures.
  If `True`, converts data into corresponding Python objects (e.g., `string`, `datetime`).

- **`mdict`**: `dict`, *optional*
  Dictionary into which MATLAB variables will be inserted. If `None`, a new dictionary is created and returned.

- **`spmatrix`**: `bool`, *optional* (default = `True`)
  Whether to read MATLAB sparse matrices as SciPy sparse matrix `coo_matrix`.

- **`**kwargs`**:
  Additional keyword arguments passed to [`scipy.io.loadmat`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html).
  These include:
  - `byte_order`
  - `mat_dtype`
  - `chars_as_strings`
  - `matlab_compatible`
  - `verify_compressed_data_integrity`
  - `variable_names`
  - `uint16_codec`

Currently, the following arguments are not supported:

- `appendmat`
- `squeeze_me`
- `struct_as_record`
- `simplify_cells`

### Example

To read subsystem data from a `.mat` file:

```python
from readmat import load_from_mat

file_path = "path/to/your/file.mat"
data = load_from_mat(file_path)
print(data)
```

**Note**: `load_from_mat()` uses a modified fork of `scipy`. The fork currently contains a few minor changes to `scipy.io` to return variable names and object metadata for all objects in a MAT-file. This change is available [on Github](https://github.com/foreverallama/scipy/tree/readmat-scipy) and can be installed directly from the branch. You can also view the changes under `patches/scipy_changes.patch` and apply it manually. Note that you might need to rebuild as parts of the Cython code was modified.

### MATLAB objects

MATLAB objects like `datetime` and `duration` are implemented using wrapper objects based on Python's `datetime`. `string` is returned as `numpy.array`. Both the processed data and raw data can be accessed and viewed.

```python
data_dict = load_from_mat(file_path)
datetime_value = data["myVarName"]["__properties__"][0, 0]

dt = datetime_value[0]  # Returns a datetime object
print(datetime_value)  # Prints datetime in readable format
```

MATLAB objects are returned as a dictionary with the following fields:

- `__class__`: The class name.
- `__properties__`: A structured `numpy.ndarray` containing the property names and their contents. Dimensions are determined by the object dimensions.
- `__default_properties__`: A structured `numpy.ndarray` containing the default values of the properties of the class (if any).
- `__s3__`: The purpose of this data is unknown, but is contained within the subsystem.
- `__s2__`: The purpose of this data is unknown, but is contained within the subsystem.

## Breakdown

A more detailed explanation of the MAT-file structure can be found [here](./docs).

## Contribution

There's still lots to do! I could use your help in the following:

- Reverse engineer the MAT-file structure to include support for more objects like `categorical`, `calendarDuration` and others
- Write object data into MAT-files
- Write tests
- Algorithmic optimization to integrate within the `scipy.io` framework
- Documentation of the MAT-file format

Feel free to create a PR if you'd like to add something, or open up an issue if you'd like to discuss! I've also opened an [issue](https://github.com/scipy/scipy/issues/22736) with `scipy.io` detailing some of the workflow, as well as a [PR](https://github.com/scipy/scipy/pull/22762) to develop this iteratively. Please feel free to contribute there as well!

## Acknowledgement

Big thanks to [mahalex](https://github.com/mahalex/MatFileHandler) for their detailed breakdown of MAT-files. Most of this wouldn't be possible without it.
