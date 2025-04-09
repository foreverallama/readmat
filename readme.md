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
```

### Reading Subsystem Data

To read subsystem data from a `.mat` file:

```python
from readmat import load_from_mat

file_path = "path/to/your/file.mat"
data = load_from_mat(file_path)
print(data)
```

**Note**: Those working with the official `scipy` release can use `read_subsystem_legacy()`. This works as `scipy.io.loadmat` only returns the last object variable in a MAT-file. This is because `loadmat` is not able to detect the array name, replacing it with a placeholder `None` which gets overwritten for each object read from file.

`load_from_mat()` uses a modified fork of `scipy`. The fork currently contains a few minor changes to `scipy.io` to return variable names and object metadata for all objects in a MAT-file. This change is available [on git](https://github.com/foreverallama/scipy/tree/readmat-scipy) and can be installed directly from the branch. You can also view the changes under `patches/scipy_changes.patch` and apply it manually. Note that you might need to rebuild as parts of the Cython code was modified.

### MATLAB objects

MATLAB objects like `datetime` and `duration` are implemented using wrapper objects based on Python's `datetime`. `string` is returned as `numpy.array`. Both the processed data and raw data can be accessed and viewed.

```python
data_dict = load_from_mat(file_path)
datetime_value = data["myVarName"]["__fields__"]

dt = datetime_value[0]  # Returns a datetime object
print(datetime_value)  # Prints datetime in readable format
```

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

## TODO

- [ ] Code cleanup for readability
- [ ] Squeeze output representation to keep it simple
- [ ] Add tests
