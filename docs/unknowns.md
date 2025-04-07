# Unknowns

This document details the unknown parts of the subsystem, and provides some hints to what they could be.

## Class Name Metadata

This is the part marked by offset 1 inside the first cell of the cell array inside the subsystem. This part usually has the format `(0, class_name_index, 0, 0)`.
Class index points to the class name from the list of all field names and class names. The remaining zeros are unknown. These could be related to types of classes, perhaps.

## Object Dependency Metadata

This is the part marked by offset 3 inside the first cell of the cell array inside the subsystem. This part usually has the format `(class_id, 0, 0, type1_id, type2_id, dependency_id)`.

- `dependency_id` basically tells us how many objects the current object __depends__ on, i.e., if the property of the object is an object itself.
- `type1_id` and `type2_id` is mostly related to how MATLAB constructs different objects. So far, I've only seen `string` type assigned as a `type_1` object. I believe this is used to flag a different type of extraction algorithm for the field contents. For e.g., `string` data is stored in a `mxUINT64` array. However, the array itself is an assortment of metadata like `ndims` followed by the actual data stored as `UTF-16` characters.
- The unknowns here are the two zeros. In all of the examples I studied, these were zero. Following the trend of the other flags, these flags could be related to the construction of special types of objects.

## Field Contents Metadata

This is the part marked by offset 2 and offset 4 inside the first cell of the cell array inside the subsystem. This part usually has the format `(field_index, 1, field_contents_id)`.

- `field_name_index` points to the field name from the list of all field names and class names
- `field_contents_index` points to the cell array containing the contents of the field
- The unknown is the flag `1`. I think this indicates the type of the field, for e.g. `hidden` or `protected` or `public`. In any case, this must be related to something about the field or property itself.

## Offset Regions 5, 6, 7 of Cell 1 Metadata

These are the parts marked by offsets 5, 6, and 7 inside the first cell of the cell array inside the subsystem. In all the examples I've studied so far, these were always all zeros.

- Region 5: A bunch of zeros of unknown purpose. Haven't been able to identify any link to the number of zeros being written as well.
- Region 6: Always non-existent. This behaviour is also observed with Region 2, which contains field contents metadata for `type 1` objects like `string`. If no `type 1` objects are in the MAT-file, then Region 2 was non-existent. Based on this information, this region could contain field contents metadata for a possible `type 3` object.
- Region 7: This was always the last 8 bytes at the end of the cell. These bytes are usually all zeros. Their purpose is unknown. It could be as simple as padding maybe.

## Cell[-3] and Cell[-2]

This is the 2nd and 3rd cell from the end of the array. No clue what these are used for.

## Why do all regions of the subsystem start with zeros or empty arrays?

This is a tricky question to answer. If you've noticed, all of the offset region starts with a bunch of zeros. In fact, within the whole of the subsystem data, there is a general trend of repeating empty elements. We can only speculate as to why, but some of the reasons could be as follows:

- Maybe someone forgot to define the ranges of the `for` loop properly? This seems highly improbable.
- They are using some kind of recursive method to write each object metadata to the file. The recursive loop ends when no more objects are available to write, resulting in a bunch of zeros.
- Some kind of padding or something for compression maybe? Dunno, perhaps.
