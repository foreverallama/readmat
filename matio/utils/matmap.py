"""Utility functions for converting MATLAB containerMap and Dictionary"""

import warnings


def mat_to_containermap(props):
    """Converts the properties of a container map to a dictionary
    MATLAB container.map:
    - Property: serialization
        - Value: struct array
            - Fields: keys, values, uniformity, keyType, valueType (default= "any")
    """
    ks = props[0, 0]["serialization"][0, 0]["keys"]
    vals = props[0, 0]["serialization"][0, 0]["values"]

    result = {}
    for i in range(ks.shape[1]):
        key = ks[0, i].item()
        val = vals[0, i]
        result[key] = val

    return result


def mat_to_dictionary(props):
    """Converts the properties of a MATLAB dictionary to a dictionary
    MATLAB dictionary:
    - Property: data
        - Value: struct array
            - Fields: Version, IsKeyCombined, IsValueCombined, Key, Value

    Wrapped as tuple of (key, value) since keys can be of any type
    """
    ver = int(props[0, 0]["data"][0, 0]["Version"].item())
    if ver != 1:
        warnings.warn(
            f"Only v1 MATLAB dictionaries are supported. Got v{ver}",
            UserWarning,
        )

    ks = props[0, 0]["data"][0, 0]["Key"].ravel()
    vals = props[0, 0]["data"][0, 0]["Value"].ravel()
    return list(zip(ks, vals))
