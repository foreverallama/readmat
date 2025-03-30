# ReadMat Module

The `readmat` module provides tools for reading and parsing `.mat` files, particularly for extracting and interpreting subsystem data. It includes utilities for handling MATLAB objects like `datetime` and `string` and converting them into Python objects.

Currently, it is a wrapper around `scipy.io` to extract field contents from an object. Currently supported objects are:
- `string` 
- `datetime`
- `duration`
- User-defined objects

**Note**: `scipy.io.loadmat` is only able to return the last object variable in a MAT-file. Hence, currently this supports reading MAT-files with only one object

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
data = read_subsystem_data(file_path)
print(data)
```

### MATLAB objects

MATLAB objects like `datetime` and `duration` are implemented using wrapper objects based on Python's `datetime`. `string` is returned as `numpy.array`. Both the processed data and raw data can be accessed and viewed.

```python
data_dict = read_subsystem_data(file_path)
datetime_value = data['datetime_array_1']['__fields__']

dt = datetime_value[0] # Returns a datetime object
print(datetime_value) # Prints datetime in readable format
```

Raw data can be accessed through its properties or using `repr()`

# Breakdown

A more detailed explanation of the MAT-file structure can be found in `docs/`

# Contribution

There's still lots to do! I could use your help in the following:
- Reverse Enginner the MAT-file structure to include support for more objects like `table` and `timetable`
- Write object data into MAT-files
- Write tests

I've also opened an [issue](https://github.com/scipy/scipy/issues/22736) with `scipy.io` and ultimately plan to push all of this over there

# Thanks

Big thanks to [mahalex](https://github.com/mahalex/MatFileHandler) for their detailed breakdown of MAT-files. Most of this wouldn't be possible without it.

# TODO:

- [x] Update `docs/`
- [x] Update `scipy.io` to extract variable names from objects
- [x] Add support for detecting object references
- [ ] Add tests for `string`, `datetime` and `duration`
- [ ] Add support for MATLAB `table` and `timetable`
- [ ] Add support for display formatting for `datetime` and `duration`
