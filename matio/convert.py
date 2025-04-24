import numpy as np

from matio.utils import (
    mat_to_categorical,
    mat_to_table,
    mat_to_timetable,
    toContainerMap,
    toDatetime,
    toDuration,
    toMatDictionary,
    toString,
)

# TODO: Add support for following classes:
# 1. dynamicprops
# 2. function_handle
# 3. event.proplistener
# 4. Function Handles
# 5. calendarDuration
# 6. timeseries
# 7. Java/.NET/COM objects
# 8. Graphics Objects


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
    }

    result = class_to_function.get(
        class_name,
        lambda: {"_Class": class_name, "_Props": props},  # Default case
    )()

    return result


def wrap_enumeration_instance(enum_array, shapes):
    """Wraps enumeration instance data into a dictionary"""
    wrapped_dict = {"_Values": np.empty(shapes, dtype=object)}
    if len(enum_array) == 0:
        wrapped_dict["_Values"] = np.array([], dtype=object)
    else:
        enum_props = [item.get("_Props", np.array([]))[0, 0] for item in enum_array]
        wrapped_dict["_Values"] = np.array(enum_props).reshape(shapes, order="F")
    return wrapped_dict
