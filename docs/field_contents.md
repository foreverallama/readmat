# Field Content Format

The contents of a field defined in its corresponding cell depends on the class and field name. It is mostly straightforward, except for some special cases, which I'll get into below. The contents of any properties not explicity defined will not be written into the MAT-file (though the field names will be present).

Field contents of object arrays of MATLAB datatypes like `string` or `datetime` are contained as arrays themselves. For example, if you define a `2x2` `datetime` array, the properties of this object array will be a `2x2` array.

<!--TOC-->

- [`datetime`](#datetime)
- [`duration`](#duration)
- [`string`](#string)
- [`table`](#table)
- [`timetable`](#timetable)
- [What if the field contains an object?](#what-if-the-field-contains-an-object)
- [The `any` Property](#the-any-property)
- [Enumeration Instance Arrays](#enumeration-instance-arrays)
- [Handle Classes](#handle-classes)

<!--TOC-->

## `datetime`

Objects of this class contain the following properties:

- `data`: A complex double precision number. The real part contains the milliseconds, and the imaginary part contains the microseconds. The date/time is calculated from the UNIX epoch
- `tmz` or Timezone: A UTF-8 string
- `fmt` or Format: The display format to use. e.g. `YYYY-MM-DD HH:MM:SS`

## `duration`

Objects of this class contain the following properties:

- `millis`: A real double precision number containing time in milliseconds
- `fmt` or Format: The display format to use. e.g. `s`, `m`, `h`, `d` for `seconds`, `minutes`, `hours`, `days`

## `string`

Objects of this class contains only one property called `any`. The contents of this property are stored as `uint64` integers. However, this needs to be decoded to extract the actual string. The data is to be read as `uint64` integers and has the following format:

- First integer most likely indicates the version of the saved `string` object
- Second integer specifies the number of dimensions `ndims`
- The next `ndims` integers specify the size of each dimension
- The next `K` integers specify the number of characters in each string in the array. Here `K` is the total number of strings in the array (which is the product of all the dimensions)
- The remaining bytes store the string contents. However, these remaining bytes are to be read as `UTF-16` characters

## `table`

Objects of this class contain the following properties:

1. `data`: A cell array, with each cell containing the values for that column
2. `ndims`: A double precision number describing the dimensions of the table, which is usually 2
3. `nrows`: A double precision number describing the number of rows in the table
4. `rownames`: A cell array. Each cell is a character array containing the row name (similar to `df.index`). If no row names are specified, this is an empty cell array
5. `nvars`: A double precision number describing the number of columns/variables
6. `varnames`: A cell array. Each cell is a character array containing the column name.
7. `props`: A `1x1` struct with the following fields, mostly containing some extended metadata:
   1. `useVariableNamesOriginal`
   2. `useDimensionNamesOriginal`
   3. `CustomProps`
   4. `VariableCustomProps`
   5. `versionSavedFrom`
   6. `minCompatibleVersion`
   7. `incompatibilityMsg`
   8. `VersionSavedFrom`
   9. `Description`
   10. `VariableNamesOriginal`
   11. `DimensionNames`
   12. `DimensionNamesOriginal`
   13. `UserData`
   14. `VariableDescriptions`
   15. `VariableUnits`
   16. `VariableContinuity`

## `timetable`

Objects of this class contains a single property `any`, which is defined as a `struct` array with the following fields:

1. `arrayProps`: A `1x1` struct with the following fields:
   1. `Description`
   2. `UserData`
   3. `TableCustomProperties`
2. `data`: A cell array, with each cell containing a variable/column values
3. `numDims`: A double precision number describing the number of dimensions of the timetable, which is usually 2
4. `dimNames`: A cell array. Each cell is a character array containing the dimension names
5. `varNames`: A cell array. Each cell is a character array containing the variable/column names.
6. `numRows`: A double precision number containing the number of rows in the timetable
7. `numVars`: A double precision number containign the number of variables/columns in the timetable
8. `varUnits`: A cell array. Each cell is a character array containing the units of the variables used
9. `rowTimes`: An array of times (typically `duration` or `datetime`). This would be an object reference to the relevant object.

The remaining fields are metadata fields:

1. `customProps`
2. `VariableCustomProps`
3. `versionSavedFrom`
4. `minCompatibleVersion`
5. `incompatibilityMsg`
6. `useVarNamesOrig`
7. `useDimNamesOrig`
8. `dimNamesOrig`
9. `varNamesOrig`
10. `varDescriptions`
11. `timeEvents`
12. `varContinuity`

## What if the field contains an object?

If the field contains an object, then the corresponding cell would contain a `uint32` column matrix structured exactly the same as the object metadata subelement of `mxOPAQUE_CLASS` in the normal part of the MAT-file. This metadata contains the `classID` and `objectID` of the object stored in its field. But how do you differentiate this from a regular `uint32` column matrix?

The answer lies in the first value of the array - the object reference. MATLAB uses the value `0xDD000000` to internally identify arrays as object metadata. This means that if you assign a `6x1` array with the first value as `0xDD000000` to a property of an object, then MATLAB tries to recognize it as an object, fails and crashes! (There are some other checks like on `ndims` to make sure it is an object reference and not a column array)

## The `any` Property

Going through different datatypes, you'll notice multiple classes contianing a property called `any`. All classes using the `any` property are defined as `type 1` objects. Most likely, these classes inherit from the same base class which is a catch all property to contain arbitrary data. So far, the following classes have been observed to use the `any` property:

- `string`
- `timetable`
- `function_handle_workspace`

## Enumeration Instance Arrays

Enumeration instance arrays are stored as `mxOPAQUE_CLASS` arrays of `MCOS` type. The object metadata for this (in the main part of the MAT-file) is returned as a `struct` array containing the following fields:

1. `EnumerationInstanceTag`: Contains the reference value `0xDD00000000`.
2. `ClassName`: A metadata indicator to extract the enumeration class name from subsystem.
3. `ValueNames`: A metadata indicator to extract the property names of the enumeration class from subsystem.
4. `Values`: Contains an array of object references, which are used to extract the contents of each instance of the enumeration array from subsytem. If the properties of the enumeration class are not initialized/instantiated, then this is an empty array.
5. `ValueIndices`: The value indices of the enumeration array. This also indicates the dimensions of the enumeration array.
6. `BuiltinClassName`: This is set if the enumeration class specifies a superclass. The value is a metadata indicator to extract the name of the superclass.

## Handle Classes

To add:

1. `dynamicprops`
2. `proplistener`
