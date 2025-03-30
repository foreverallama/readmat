# ReadMat Module

The `readmat` module provides tools for reading and parsing `.mat` files, particularly for extracting contents from user-defined objects or MATLAB datatypes such as `datetime`, `table` and `string`. It uses a wrapper built around `scipy.io` to extract raw subsystem data from MAT-files, which is then parsed and interpreted to extract object data. It includes utilities for reading MATLAB objects like `datetime` and `duration` both as raw data or their respective Python objects. 

 Currently supported MATLAB objects are:

- `string` 
- `datetime`
- `duration`
- `table`
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
from readmat import read_subsystem_data

file_path = "path/to/your/file.mat"
data = read_subsystem_data_(file_path)
print(data)
```

**Note**: Those working with the official `scipy` release can use `read_subsystem_legacy()`. This works as `scipy.io.loadmat` only returns the last object variable in a MAT-file. This is because `loadmat` is not able to detect the array name, replacing it with a placeholder `None` which gets overwritten for each object read from file.

`read_subsystem_data()` uses a modified fork of `scipy`, which I've included as a submodule. The fork currently contains changes to `scipy.io` to return variable names for all objects in a MAT-file. I'm looking to integrate a large part of this code base with `scipy.io` over the next couple of weeks.

### MATLAB objects

MATLAB objects like `datetime` and `duration` are implemented using wrapper objects based on Python's `datetime`. `string` is returned as `numpy.array`. Both the processed data and raw data can be accessed and viewed.

```python
data_dict = read_subsystem_data(file_path)
datetime_value = data['myVarName']['__fields__']

dt = datetime_value[0] # Returns a datetime object
print(datetime_value) # Prints datetime in readable format
```

Raw data can be accessed through its properties or using `repr()`

# Breakdown

A more detailed explanation of the MAT-file structure can be found [here](./docs).

# Contribution

There's still lots to do! I could use your help in the following:

- Reverse engineer the MAT-file structure to include support for more objects like `timetable`, `categorical`, `calendarDuration` and others
- Write object data into MAT-files
- Write tests
- Algorithmic optimization to integrate within the `scipy.io` framework

I've also opened an [issue](https://github.com/scipy/scipy/issues/22736) with `scipy.io` detailing some of the workflow, as well as a [PR](https://github.com/scipy/scipy/pull/22762) to develop this iteratively.

# Thanks

Big thanks to [mahalex](https://github.com/mahalex/MatFileHandler) for their detailed breakdown of MAT-files. Most of this wouldn't be possible without it.

# TODO:

- [x] Update `docs/`
- [x] Add support for detecting object references
- [x] Update `scipy.io` to extract variable names from objects
- [x] Added support for MATLAB `table` as raw data
- [x] Add `scipy` fork as a submodule
- [ ] Wrap MATLAB `table` within a Pandas DataFrame
- [ ] Update `scipy.io` to include object reference checks inside `read_real_complex()` 
- [ ] Add tests for `string`, `datetime`, `duration` and `table`
- [ ] Add support for MATLAB `timetable`
- [ ] Add support for display formatting for `datetime` and `duration`
