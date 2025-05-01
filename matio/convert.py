"""Convert MATLAB objects to Python compatible objects"""

from enum import Enum

import numpy as np

from matio.utils import (
    mat_to_calendarduration,
    mat_to_categorical,
    mat_to_containermap,
    mat_to_datetime,
    mat_to_dictionary,
    mat_to_duration,
    mat_to_string,
    mat_to_table,
    mat_to_timetable,
)

CLASS_TO_FUNCTION = {
    "datetime": mat_to_datetime,
    "duration": mat_to_duration,
    "string": mat_to_string,
    "table": mat_to_table,
    "timetable": mat_to_timetable,
    "containers.Map": lambda props, **kwargs: {
        "_Class": "containers.Map",
        "_Props": mat_to_containermap(props),
    },
    "categorical": mat_to_categorical,
    "dictionary": mat_to_dictionary,
    "calendarDuration": mat_to_calendarduration,
}


def convert_to_object(
    props, class_name, byte_order, raw_data=False, add_table_attrs=False
):
    """Converts the object to a Python compatible object"""

    if raw_data:
        return {
            "_Class": class_name,
            "_Props": props,
        }

    func = CLASS_TO_FUNCTION.get(
        class_name,
        lambda props, **kwargs: {
            "_Class": class_name,
            "_Props": props,
        },
    )

    return func(props, byte_order=byte_order, add_table_attrs=add_table_attrs)


def mat_to_enum(values, value_names, class_name, shapes):
    """Converts MATLAB enum to Python enum"""

    enum_class = Enum(
        class_name,
        {name: val["_Props"].item() for name, val in zip(value_names, values)},
    )

    enum_members = [enum_class(val["_Props"].item()) for val in values]
    return np.array(enum_members, dtype=object).reshape(shapes, order="F")
