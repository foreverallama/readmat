def toContainerMap(props):
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
