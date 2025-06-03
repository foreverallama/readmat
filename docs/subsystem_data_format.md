# Subsystem Data Format

<!--TOC-->

- [Basic File Header](#basic-file-header)
- [Data Element 1: mxStruct_CLASS](#data-element-1-mxstructclass)
  - [Data Subelement: mxOPAQUE_CLASS](#data-subelement-mxopaqueclass)
  - [Cell 1 - Linking Metadata](#cell-1---linking-metadata)
    - [Region 1: Class Identifiers](#region-1-class-identifiers)
    - [Region 3: Object Identifiers](#region-3-object-identifiers)
    - [Region 4: Type 2 Object Property Identifiers](#region-4-type-2-object-property-identifiers)
    - [Region 2: Type 1 Object Property Identifiers](#region-2-type-1-object-property-identifiers)
    - [Region 5: Dynamic Property Metadata](#region-5-dynamic-property-metadata)
    - [Other Regions](#other-regions)
  - [Cell 2 - Padding](#cell-2---padding)
  - [Field Content Cells](#field-content-cells)
  - [Remaining Cells](#remaining-cells)
- [Data Element 2: Character Array](#data-element-2-character-array)

<!--TOC-->

If you remember, the MAT-file header contains a field called `Subsystem Offset`. This is essentially a byte marker to another region of the MAT-file, which is the subsystem data. This appears as a normal data element in the MAT-file (typically the last data element in file). This data element is stored as `mxUINT8_CLASS` values, and does **not** have an array name. The subsystem data is contained within the real part of this data element.

The data within this element is formatted like a MAT-file itself, and contains information about all objects stored in the MAT-file, along with their contents. It has the following structure:

```text
├──Basic File Header
├── Data Element: mxSTRUCT_CLASS
│   ├── Field "MCOS": mxOPAQUE_CLASS
        ├── Class "FileWrapper__"
        ├── Type: "MCOS"
        ├── Metadata: Cell Array
            ├── Cell 1
            ├── Cell 2
            ├── Cell 3
            ├── Cell 4
            .
            .
            .
            ├── Cell (3 + N)
            ├── Cell (3 + N) + 1
            ├── Cell (3 + N) + 2
            ├── Cell (3 + N) + 3
    ├── Field "java"
├── Data Element: Character Array
```

An accompanying [excel sheet](./ss_data_breakdown.xlsx) depicting the subsystem data format is attached to help with understanding.

## Basic File Header

This is a basic version of the file header of the actual MAT-file, mentioning only the MAT-file version and Endianness.This information is contained in the first 4 bytes, which is usually `0x01 0x00` followed by `MI` if big endian (and reversed if little endian). Then 4 bytes of padding are applied to align it to an 8 byte boundary.

## Data Element 1: mxStruct_CLASS

The first data element is of `mxSTRUCT_CLASS`. This is a `1 x 1` struct array which has fields set based on the type system of the `mxOPAQUE_CLASS` variables in the MAT-file. The field names of this struct is the same as the type system names. For example, `MCOS` types will contain a field `MCOS`. For `java` types, this will contain a field `java`.

### Data Subelement: mxOPAQUE_CLASS

The `MCOS` field contains an array of type `mxOPAQUE_CLASS`, which contains all the information we need. This subelement is quite similar to the data element that appears in the normal part of the MAT-file, but with some key differences:

- The subelement does not have an array name
- The subelement is of class type `FileWrapper__`
- The object metadata is a `mxCELL_CLASS` array

This cell array is what we need to look at closely. The cell array has a dimension `(N + 5, 1)`, where $N = \sum_{\text{objects}} \text{(number of properties of object)}$. The first cell in the array contains some metadata. The second cell is empty of size `0 bytes`, whose purpose is unknown. The third cell onwards contains the contents of each field for every object in the MAT-file, stored as a regular data element. Finally, there are 3 more cells in the array that appear at the end, which contain some properties of each class in the MAT-file. This structure is visualized below.

| Cell Array Index | fieldContentID | Cell Content |
|-----------|-----------|-----------|
| 1 | - | Metadata |
| 2 | - | Empty Cell |
| 3 | 0 | Object Property Contents |
| 4 | 1 | Object Property Contents |
| . | . | . |
| . | . | . |
| N + 3 | N | Object Property Contents |
| N + 4 | - | Unknown |
| N + 5 | - | Unknown |
| N + 6 | - | Default Class Properties |

### Cell 1 - Linking Metadata

The data in this cell is stored as a `mxUINT8` data element. However, the actual data consists of a combination of `int8` integers and `uint32` (or maybe `int32`) integers. The contents consist of a large series of different types of metadata, ordered as follows:

- `Version Indicator`: 32-bit integer indicating the version of `FileWrapper__` metadata. Afaik, the latest version is `4`.
- `num_strings`: 32-bit integer indicating the total number of unique fields and classes of all objects in the MAT-file
- `offsets`: A list of **eight** 32-bit integers, which are byte markers to different regions within this cell. The byte marker is relative to the start of the cell's data.
- `names`: A list of null-terminated `int8` characters indicating all field and class names (in no particular order)

#### Region 1: Class Identifiers

- The start of this region is indicated by the first offset value
- This region consists of blocks of **four** 32-bit integers in the format `(handle_class_name_index, class_name_index, 0, 0)`
- The value `class_name_index` points to the class name in the list `names` obtained above
- The value `namespace_index` points to the namespace in the list of `names` obtained above. For more information, see [namespaces](https://in.mathworks.com/help/matlab/matlab_oop/namespaces.html)
- The first block is always all zeros
- The blocks are ordered by `classID`

#### Region 3: Object Identifiers

- The start of this region is indicated by the third offset value
- This region consists of blocks of **six** 32-bit integers in the format `(classID, 0, 0, type1_ID, type2_ID, object_dependency_id)`
- These blocks are ordered by `objectID`
- The first block is always all zeros
- `classID` is the same values assigned to the object array in the normal MAT-file
- `object_dependency_id` is used to identify nested objects. The value in this field indicates the `object_id` **upto** which it depends on.
- `type1ID` and `type2ID` are linked to different types of objects. For example, `string` is a `type1` object, whereas `datetime` is a `type2` object
- Each `type1` and `type2` object is assigned a unique ID, in order of `objectID`, starting from one

#### Region 4: Type 2 Object Property Identifiers

- The start of this region is indicated by the fourth offset value
- This region consists of blocks of 32-bit integers, in order of `type2_id`
- Each block is padded to an 8 byte boundary
- The first block is always all zeros
- The size of each block is determined by the first 32-bit integer.
- The first 32-bit integer indicates the number of sub-blocks for each block
- Each sub-block is of the format `(field_name_index, field_type, field_value)`
  - The value `field_name_index` points to the field name in the list `names` obtained above
  - `field_type` indicates whether the field is a property or an attribute
    - `field_type = 0` indicates an enumeration member
    - `field_type = 1` indicates a property
    - `field_type = 2` indicates an attribute like `Hidden`, `Constant`, etc.
  - `field_value` depends on `field_type`
    - If `field_type = 0`, `field_value` contains the index of the field name in linking metadata. These fields store the field name as a character array. The name refers to an enumeration.
    - If `field_type = 1`, `field_value` contains the index of the cell in the cell array containing the property contents. The indexing here starts from zero. However, it should be noted that the 0th index points to Cell 3 of the cell array.
    - If `field_type = 2`, `field_value` contains the actual value itself. MATLAB internally decodes this based on the attribute type

#### Region 2: Type 1 Object Property Identifiers

This region is structured exactly the same as _Region 4_, but is for Type 1 objects. The start of this region is indicated by the second offset value. Type 1 objects use a `saveobj` method that defines how the object is saved to a MAT-file. If the contents being saved does not correspond to an object of the same class, then it is indicated as a `Type 1` object.

For example, if a class `MyClass` uses a `saveobj` method that returns a `struct`, then it is saved as a `Type 1` object. Objects of this type are stored using a property name `any`. So far, the following MATLAB datatypes have been observed to use this type:

- `string`
- `timetable`
- `function_handle_workspace`

#### Region 5: Dynamic Property Metadata

This region links objects to any dynamic properties it contains (probably eventlisteners as well).

- The start of this region is indicated by the fifth offset value
- This region consists of blocks of 32-bit integers, in order of `dependency_id`
- Each block is of the form `(num_dynamic_properties, prop_id_1, prop_id_2 ...., prop_id_N)`
- Here, `prop_id` points to the `type2_id` of the dynamic property
- Each block is padded to 8 byte boundary
- The first block is all zeros

#### Other Regions

The 6th and 7th offset values indicate other metadata regions whose purpose is unknown. These offsets are apparently not present/reserved in earlier version of `FileWrapper__` metadata, and is probably related to the handling of certain special types of objects.

The last offset points to the end of this cell.

### Cell 2 - Padding

Cell 2 is always tagged as `miMATRIX` of `0 bytes`. This is most likely used to pad between metadata cells and field content cells. It's actual purpose is unknown.

### Field Content Cells

Field contents are stored from Cell 3 onwards. The data element used to store field contents depend on the class and field types. A breakdown of field content datatypes for some common MATLAB fields can be read [here](./field_contents.md)

### Remaining Cells

There are always three more cells at the end of the array, which appear after all the field content cells. These cells contain some data related to each class. The purpose of these cells is partially unknown.

- Cell[-3] is a cell array of `(num_classes + 1, 1)` dimensions, in order of `class_id`. Each cell is written in place as a struct. The contents of this struct is unknown, and is usually empty. The first cell is always an empty struct array.
- Cell[-1] has the same format as Cell[-3]. This cell contains a list of default property values assigned within the class. The fields of each struct are the property names, and the field contents correspond to the default property values.
- Cell[-2] is instead a `mxINT32` array of `(num_classes + 1, 1)` dimensions, in order of `class_id`. The first integer is always zero. Its purpose is unknown, and is usually all zeros. Modifying these values does not seem to affect reading/writing of MAT-files.

## Data Element 2: Character Array

Finally, the last part of the subsystem data contains another data element which is stored as a `mxUINT8` character array. However, the contents of this array is again structured like a mini-MAT file like the subsystem data itself, except as an empty struct. Note that this element is not always present. My guess is MATLAB is using some kind of recursive function to write the subsystem data, popping out objects from a buffer as they are written, resulting in this empty data element at the end.

There are still quite a few unknowns which could use some reverse engineering. I have detailed these in [unknowns.md](./unknowns.md). If anyone wants to contribute to this, pelase do open an issue!
