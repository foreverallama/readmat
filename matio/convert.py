import numpy as np

from matio.utils import toDataFrame, toDatetime, toDuration, toString

# TODO: Add support for following classes:
# 1. dynamicprops
# 2. function_handle
# 3. event.proplistener


def convert_to_object(props, class_name, byte_order, raw_data=False):
    """Converts the object to a Python compatible object"""

    if raw_data:
        result = {
            "_Class": class_name,
            "_Props": props,
        }
        return result

    if class_name == "datetime":
        result = toDatetime(props)

    elif class_name == "duration":
        result = toDuration(props)

    elif class_name == "string":
        result = toString(props, byte_order)

    elif class_name == "table":
        result = toDataFrame(props)

    elif class_name == "timetable":
        return props

    else:
        # For all other classes, return raw data
        result = {
            "_Class": class_name,
            "_Props": props,
        }

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
