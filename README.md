# Mat-IO Module

The `mat-io` module provides tools for reading `.mat` files, particularly for extracting contents from user-defined objects or MATLAB datatypes such as `datetime`, `table` and `string`. It uses a wrapper built around `scipy.io` to extract raw subsystem data from MAT-files, which is then parsed and interpreted to extract object data.

`mat-io` can read almost all types of objects from MAT-files, including user-defined objects. Additionally, it includes utilities to convert the following MATLAB datatypes into their respective _Pythonic_ objects:

- `string`
- `datetime`, `duration` and `calendarDuration`
- `table` and `timetable`
- `containers.Map` and `dictionary`
- `categorical`
- Enumeration Instance Arrays

**Note**: `load_from_mat()` uses a modified fork of `scipy`. The fork currently contains a few minor changes to `scipy.io` to return variable names and object metadata for all objects in a MAT-file. This change is available [on Github](https://github.com/foreverallama/scipy/tree/readmat-scipy) and can be installed directly from the branch. You can also view the changes under `patches/scipy_changes.patch` and apply it manually. Note that you might need to rebuild as parts of the Cython code was modified. Follow the instruction on the [official SciPy documentation](https://scipy.github.io/devdocs/building/index.html#building-from-source).

## Usage

Install using pip

```bash
pip install mat-io
```

### Example

To read subsystem data from a `.mat` file:

```python
from matio import load_from_mat

file_path = "path/to/your/file.mat"
data = load_from_mat(file_path, raw_data=False, add_table_attrs=False)
print(data)
```

#### Parameters

- **`file_path`**: `str`
  Full path to the MAT-file.

- **`raw_data`**: `bool`, *optional*
  - If `False` (default), returns object data as raw object data
  - If `True`, converts data into respective Pythonic datatypes (e.g., `string`, `datetime` and `table`).

- **`add_table_attrs`**: `bool`, *optional*
  If `True`, additional properties of MATLAB `table` and `timetable` are attached to the resultant `pandas.DataFrame`. Works only if `raw_data = False`

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

### MATLAB objects

MATLAB objects are returned as a dictionary with the following fields:

- `_Class`: The class name
- `_Props`: A structured `numpy.ndarray` containing the property names and their contents. Dimensions are determined by the object dimensions.

If the `raw_data` parameter is set to `False`, then `load_from_mat` converts these objects into a corresponding Pythonic datatype. This conversion is [detailed here](https://github.com/foreverallama/matio/tree/main/docs).

## Contribution

There's still lots to do! I could use your help in the following:

- Reverse engineer the MAT-file structure to include support for more objects like `categorical`, `calendarDuration` and others
- Write object data into MAT-files
- Write tests
- Algorithmic optimization to integrate within the `scipy.io` framework
- Documentation of the MAT-file format

Feel free to create a PR if you'd like to add something, or open up an issue if you'd like to discuss! I've also opened an [issue](https://github.com/scipy/scipy/issues/22736) with `scipy.io` detailing some of the workflow, as well as a [PR](https://github.com/scipy/scipy/pull/22847) to develop this iteratively. Please feel free to contribute there as well!

## Acknowledgement

Big thanks to [mahalex](https://github.com/mahalex/MatFileHandler) for their detailed breakdown of MAT-files. A lot of this wouldn't be possible without it.
