# Unknowns

This document details the unknown parts of the subsystem, and provides some hints to what they could be.

## Class Name Metadata

This is the part marked by offset 1 inside the first cell of the cell array inside the subsystem. This part usually has the format `(handle_class_name_index, class_name_index, 0, 0)`.
`class_name_index` and `handle_class_name_index` point to class names from the list of all field names and class names. The remaining zeros are unknown. These could be related to other types of classes, perhaps.

## Object Dependency Metadata

This is the part marked by offset 3 inside the first cell of the cell array inside the subsystem. This part usually has the format `(class_id, 0, 0, type1_id, type2_id, dependency_id)`.

- `dependency_id` basically tells us how many objects the current object __depends__ on, i.e., if the property of the object is an object itself.
- `type1_id` and `type2_id` is mostly related to how MATLAB constructs different objects. So far, I've only seen `string` type assigned as a `type_1` object. I believe this is used to flag a different type of extraction algorithm for the field contents. For e.g., `string` data is stored in a `mxUINT64` array. However, the array itself is an assortment of metadata like `ndims` followed by the actual data stored as `UTF-16` characters.
- The unknowns here are the two zeros. In all of the examples I studied, these were zero. Following the trend of the other flags, these flags could be related to the construction of special types of objects.

## Field Contents Metadata

This is the part marked by offset 2 and offset 4 inside the first cell of the cell array inside the subsystem. This part usually has the format `(field_index, field_type, field_value)`.

- `field_name_index` points to the field name from the list of all field names and class names
- `field_type` indicates if the field is a property (1) or an attribute (2). It is unclear if there are more types.
- `field_value` depends on the flag set by `field_type`
  - If `field_value = 1`, then it points to the cell array containing the property values
  - If `field_value = 2`, then it is a logical value, i.e., either `true` or `false`

## Offset Regions 5, 6, 7 of Cell 1 Metadata

These are the parts marked by offsets 6, and 7 inside the first cell of the cell array inside the subsystem. In all the examples I've studied so far, these were always all zeros.

- Region 6: Always non-existent. This behaviour is also observed with Region 2, which contains field contents metadata for `type 1` objects like `string` which use the `any` property. If no `type 1` objects are in the MAT-file, then Region 2 was non-existent. Based on this information, this region could contain field contents metadata for a possible `type 3` object.
- Region 7: This was always the last 8 bytes at the end of the cell. These bytes are usually all zeros. Their purpose is unknown. It could be as simple as padding maybe.

## Cell[-3] and Cell[-2]

Cell[-3] has the same structure as Cell[-1], i.e., it consists of a `(num_classes + 1, 1)` cell array, where `num_classes` is the number of classes in the MAT-file. Going by Cell[-1], it can be deduced that these structs are ordered by `class_id`, with an first cell being empty. Each cell is in turn a `struct`. Its contents are unknown, but likely contains some kind of class related instantiations.

Cell[-2] is a `mxINT32` array with dimensions `(num_classes + 1, 1)`. Both the integers were zero. Its purpose is unknown. Manipulating these integers did not seem to affect MAT-files.

## Why do all regions of the subsystem start with zeros or empty arrays?

This is a tricky question to answer. If you've noticed, all of the offset region starts with a bunch of zeros. In fact, within the whole of the subsystem data, there is a general trend of repeating empty elements. We can only speculate as to why, but some of the reasons could be as follows:

- Maybe someone forgot to define the ranges of the `for` loop properly? This seems highly improbable.
- They are using some kind of recursive method to write each object metadata to the file. The recursive loop ends when no more objects are available to write, resulting in a bunch of zeros.
- Some kind of padding or something for compression maybe? Dunno, perhaps.
