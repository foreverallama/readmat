from enum import Enum

import numpy as np

from matio.utils import (
    mat_to_calendarDuration,
    mat_to_categorical,
    mat_to_table,
    mat_to_timetable,
    toContainerMap,
    toDatetime,
    toDuration,
    toMatDictionary,
    toString,
)


def convert_to_object(
    props, class_name, byte_order, raw_data=False, add_table_attrs=False
):
    """Converts the object to a Python compatible object"""

    if raw_data:
        return {
            "_Class": class_name,
            "_Props": props,
        }

    class_to_function = {
        "datetime": lambda: toDatetime(props),
        "duration": lambda: toDuration(props),
        "string": lambda: toString(props, byte_order),
        "table": lambda: mat_to_table(props, add_table_attrs),
        "timetable": lambda: mat_to_timetable(props, add_table_attrs),
        "containers.Map": lambda: {
            "_Class": class_name,
            "_Props": toContainerMap(props),
        },
        "categorical": lambda: mat_to_categorical(props),
        "dictionary": lambda: toMatDictionary(props),
        "calendarDuration": lambda: mat_to_calendarDuration(props),
    }

    result = class_to_function.get(
        class_name,
        lambda: {"_Class": class_name, "_Props": props},  # Default case
    )()

    return result


def mat_to_enum(values, value_names, class_name, shapes):
    """Converts MATLAB enum to Python enum"""

    enum_class = Enum(
        class_name,
        {name: val["_Props"].item() for name, val in zip(value_names, values)},
    )

    enum_members = [enum_class(val["_Props"].item()) for val in values]
    return np.array(enum_members, dtype=object).reshape(shapes, order="F")
