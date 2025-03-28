# Subsystem Data Format

If you remember, the MAT-file header contains a field called `Subsystem Offset`. This is essentially a byte marker to another region of the MAT-file, which is the subsystem data. This appears as a normal data element in the MAT-file (typically the last data element in file). This data element is stored as `mxUINT8_CLASS` values, and does **not** have an array name. The subsystem data is contained within the real part of this data element.

The data within this element is formatted like a MAT-file itself, and contains information about all objects stored in the MAT-file, along with their contents. It has the following structure:

```
├──Basic File Header
├── Data Element: mxSTRUCT_CLASS
│   ├── Field "MCOS": Cell Array
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
├── Data Element: Character Array
```

An accompanying [excel sheet](./ss_data_breakdown.xlsx) depicting the subsystem data format is attached to help with understanding.

## Basic File Header

This is a basic version of the file header of the actual MAT-file, mentioning only the MAT-file version and Endianness.This information is contained in the first 4 bytes, which is usually `0x01 0x00` followed by `MI` if big endian (and reversed if little endian). Then 4 bytes of padding are applied to align it to an 8 byte boundary.

## Data Element 1: mxStruct_CLASS

The first data element is of `mxSTRUCT_CLASS`, which has a single field called `MCOS`. This field contains an array of type `mxOPAQUE_CLASS`, which contains all the information we need.

### Data Subelement: mxOPAQUE_CLASS

This subelement is quite similar to the data element that appears in the normal part of the MAT-file, but with some key differences:
- The subelement does not have an array name
- The subelement is of class type `FileWrapper__`
- The object metadata is **not** a `mxUINT32` array, but instead a `mxCELL_CLASS` array

This cell array is what we need to look at closely. The cell array has a dimension `(N + 5, 1)`, where $N = \sum_{\text{objects}} \text{(number of properties of object)}$. The first cell in the array contains some metadata. The second cell is empty of size `0 bytes`, and is most likely used for padding. The third cell onwards contains the contents of each field for every object in the MAT-file, stored as a regular data element. Finally, there are 3 more cells in the array that appear at the end, the purpose of which is not known yet. This structure is visualized below. 

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
| N + 6 | - | Unknown |

Note the column `fieldContentID`. The cell containing field contents are also IDed indexed from `0`. This will be used later to link field contents to its corresponding field name.

### Cell 1 - Linking Metadata

The data in this cell is stored as a `mxUINT8` data element. However, the actual data consists of a combination of `uint8` values and `uint32` values, and must be parsed as raw data. The contents consist of a large series of different types of metadata, ordered as follows:

- `Header`: 32-bit integer with unknown significance
- `num_fields_classes`: 32-bit integer indicating the total number of unique fields and classes of all objects in the MAT-file
- `offsets`: A list of **eight** 32-bit integers, which are byte markers to different regions within this cell. The byte marker is relative to the start of the cell's data
- `names`: A list of null-terminated `int8` strings indicating all field and class names (in no particular order)
- A bunch of different regions indicated by `offsets`

#### Region 1: Class Identifier Metadata

- The start of this region is indicated by the first offset value
- This region consists of blocks of **four** 32-bit integers in the format `(0, class_name_index, 0, 0)`
- The value `class_name_index` points to the class name in the list `names` obtained above
- The first block is always all zeros
- The blocks are ordered by `classID`

#### Region 3: Object Identifier Metadata

- The start of this region is indicated by the third offset value
- This region consists of blocks of **six** 32-bit integers in the format `(classID, 0, 0, type1_ID, type2_ID, objectID)`
- These blocks are ordered by `objectID`
- The first block is always all zeros
- `classID` and `objectID` are the same values assigned to the object array in the normal MAT-file
- `type1ID` and `type2ID` are linked to different types of objects. For example, `string` is a `type1` object, whereas `datetime` is a `type2` object
- Each `type1` and `type2` object is assigned a unique ID, in order of `objectID`, starting from zero

#### Region 2: Type 1 Object Metadata

- The start of this region is indicated by the second offset value
- This region consists of blocks of 32-bit integers, in order of `type1_id`
- Each block is padded to an 8 byte boundary
- The first block is always all zeros
- The size of each block is determined by the first 32-bit integer.
- The first 32-bit integer indicates the number of sub-blocks for each block
- Each sub-block is of the format `(field_name_index, 1, fieldContentID)`
- The value `field_name_index` points to the field name in the list `names` obtained above
- The value `fieldContentID` points to the index of the cell array containing the contents of this field

#### Region 4: Type 2 Object Metadata

This region is structured exactly the same as _Region 2_, but is for Type 2 objects. The start of this region is indicated by the fourth offset value.

#### Other Regions

The 5th, 6th and 7th offset values indicate other metadata regions whose purpose is unknown. The last offset points to the end of this cell. 

### Cell 2 - Padding

Cell 2 is always tagged as `miMATRIX` of `0 bytes`. This is most likely used to pad between metadata cells and field content cells.

### Field Content Cells

Field contents are stored from Cell 3 onwards. The data element used to store field contents depend on the class and field types. A breakdown of field content datatypes for some common MATLAB fields can be read [here](./field_contents.md)

### Remaining Cells

There are always three more cells at the end of the array, which appear after all the field content cells. The purpose of these cells are unknown. They are typically empty cells, but might contain some kind of metadata for MATLAB datatypes.

## Data Element 2: Character Array

Finally, the last part of the subsystem data contains another data element which is stored as a `mxUINT8` character array. However, the contents of this array is again structured like a mini-MAT file like the subsystem data itself. 

The data within this element contains a 4 byte header indicating MAT-file version and Endianness, and a single data element of `mxSTRUCT` type. This data element contains a single field `MCOS`. However, the contents of this field are empty. 

My guess is MATLAB is using some kind of recursive function to write the subsystem data, popping out objects from a buffer as they are written, resulting in this empty data element at the end.
