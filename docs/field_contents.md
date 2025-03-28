# Field Content Format

The contents of a field defined in its corresponding cell depends on the class and field name. It is mostly straightforward, except for some special cases, which I'll get into below. The contents of any properties not explicity defined will not be written into the MAT-file (though the field names will be present).

Field contents of object arrays of MATLAB datatypes like `string` or `datetime` are contained as arrays themselves. For example, if you define a `2x2` `datetime` array, the properties of this object array will be a `2x2` array.

## `datetime`

Objects of this class contain the following properties:

- `data`: A complex double precision number. The real part contains the milliseconds, and the imaginary part contains the microseconds. The date/time is calculated from the UNIX epoch
- `tmz` or Timezone: A UTF-8 string
- `fmt` or Format: The display format to use. e.g. `YYYY-MM-DD HH:MM:SS`

## `duration`:

Objects of this class contain the following properties:

- `millis`: A real double precision number containing time in milliseconds
- `fmt` or Format: The display format to use. e.g. `s`, `m`, `h`, `d` for `seconds`, `minutes`, `hours`, `days`

## `string`:

Objects of this class contains only one property called `any`. The contents of this property are stored as `uint64` integers. However, this needs to be decoded to extract the actual string. The data is to be read as `uint64` integers and has the following format:

- First integer of unknown purpose
- Second integer specifies the number of dimensions `ndims`
- The next `ndims` integers specify the size of each dimension
- The next `K` integers specify the number of characters in each string in the array. Here `K` is the total number of strings in the array (which is the product of all the dimensions)
- The remaining bytes store the string contents. However, these remaining bytes are to be read as `UTF-16` characters

## What if the field contains an object?

If the field contains an object, then the corresponding cell would contain a `uint32` column matrix structured exactly the same as the object metadata subelement of `mxOPAQUE_CLASS` in the normal part of the MAT-file. This metadata contains the `classID` and `objectID` of the object stored in its field. But how do you differentiate this from a regular `uint32` column matrix?

The answer lies in the first value of the array - the object reference. MATLAB uses the value `0xDD000000` to internally identify arrays as object metadata. This means that if you assign a `6x1` array with the first value as `0xDD000000` to a property of an object, then MATLAB tries to recognize it as an object, fails and crashes! (There are some other checks like on `ndims` to make sure it is an object reference and not a column array)