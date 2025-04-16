# MAT-file Format

The MAT-file format is well documented [here](https://www.mathworks.com/help/pdf_doc/matlab/matfile_format.pdf), so I won't be going into details. Most of this is already implemented within `scipy.io.matlab`. However, MATLAB has not included documentation for decoding objects. These objects could be user-defined classes, or MATLAB datatypes like `string`, `datetime`, `table`, etc. Reading this information from `.mat` files is currently not implemented within `scipy.io`, hence decoding and understanding the format is the first step to extract object information.

<!--TOC-->

- [The Basics](#the-basics)
- [mxOPAQUE_CLASS Data Element](#mxopaqueclass-data-element)
  - [Array Flags Subelement](#array-flags-subelement)
  - [Array Name](#array-name)
  - [Type System Name](#type-system-name)
  - [Class Name](#class-name)
  - [Object Metadata](#object-metadata)
    - [Reference Value](#reference-value)
    - [Dimensions Array](#dimensions-array)
    - [Object ID](#object-id)
    - [Class ID](#class-id)
- [Subsystem Data](#subsystem-data)

<!--TOC-->

## The Basics

Here I'll give a brief overview of the MAT-file format. For more details you can refer to the documentation. You can skip to the next section if you're already familiar with this.

- Every MAT-file consists of a 128-byte header
  - The first 116 bytes contains some text
  - The next 8 bytes contains `Subsystem Offset Information`. This is a byte marker to another region in the MAT-file
  - The last 4 bytes contain information about MAT-file version and Endian indicator

- Each variable (or data element) stored in the MAT-file appear after this header, usually ordered by their variable names
  - Each data element has an 8 byte tag, followed by its data
  - Since MATLAB tags all variables as arrays/matrices, this tag should indicate the data element as a `miMATRIX` or `miCOMPRESSED` if file compression was enabled
  - Additionally, the tag mentions the number of bytes to read for the data element

- Depending on the data type, the data element consists of different sub headers.
  - The first 16 bytes, called `Array Flag`, identifies the datatype of the data element.
  - The following bytes contain some additional information like `array name`, `array dimensions`, `field names` if its a `struct`, etc. The documentation goes into this in detail.
  - Finally, the last part of this data element contains the actual data in the array corresponding to its datatype.

If you look at the documentation in `Table 1-3`, you'll notice only 15 MATLAB array types are mentioned. However, there are at least 2 more, with the last one being `mxOPAQUE_CLASS` which is what we are interested in.

## mxOPAQUE_CLASS Data Element

An `Array Flag` value of `17` identifies the data element as an `mxOPAQUE_CLASS` array. This array type has the following structure:

| Subelement  | Data Type  | Number of Bytes  |
|-----------|-----------|-----------|
| Array Flags | miUNT32 | 2 * sizeOfDataType (8 bytes) |
| Array Name | miINT8 | numberOfCharacters * sizeOfDataType |
| Type System Name | miINT8 | numberOfCharacters * sizeOfDataType (4 bytes) |
| Class Name | miINT8 | numberOfCharacters * sizeOfDataType |
| Object Metadata | Object metadata is written as a miUINT32 array |

**Note**: Each subelement is padded to an 8 byte block

### Array Flags Subelement

This subelement identifies the MATLAB array type. For `mxOPAQUE_CLASS`, the class type is set to `17`

### Array Name

This subelement specifies the name assigned to the array, as an array of signed, 8-bit values.

### Type System Name

This subelement identifies the type system of the `mxOPAQUE_CLASS` data element as `miINT8` characters. For datatypes like `datetime`, `string`, and most user-defined objects, the type system is `MCOS` or MATLAB Class Object System. Another known type system is `java` for Java objects.

### Class Name

This subelement identifies the class which the object array belongs to. The class name is stored as an array of signed, 8-bit values.

### Object Metadata

The structure of the object metadata depends on the type of object. For `MCOS` objects, these could be either `uint32` or `struct` arrays (as far as I know). Regardless, the actual contents of the object is indicated by an **object reference** which is a `miUINT32` array. This can be read as a data subelement, and usually contains the following:

| Subelements | Number of Bytes |
|-----------|-----------|
| Object Reference | 4 bytes |
| Dimensions Array | numberOfDimensions * 4 bytes |
| Object ID | numObjectsInArray * 4 bytes |
| Class ID | 4 bytes |

#### Reference Value

This contains the value `0xDD000000` which is used internally by MATLAB to identify data elements as objects (explained later in detail)

#### Dimensions Array

The first value of the array indicates the number of dimensions (`ndims`) of the object array, and the next `ndim` integers list the size of each dimension. For example, if its a single object, this subelement would contain the values `2, 1, 1`. We typically deal with 2D arrays, hence `ndims` is usually 2.

#### Object ID

This contains a list of integers which serves as a unique identifiers for the object. All objects in a MAT-file are given an object ID, which will be used later to extract its contents. Object IDs are numbered starting from `1`. Object arrays are treated as a collection of object instances, hence each instance in the array is assigned an object ID. In this case, the object ID would be a list of integers, the length of which would be indicated by the dimensions array.

#### Class ID

This contains a number which servers as a unique identifier for the class type of an object. All objects in a MAT-file are associated with a class ID to identify the class they belong to. Class IDs are numbered starting from `1`.

## Subsystem Data

I'll talk about this in more detail [here](./subsystem_data_format.md)
