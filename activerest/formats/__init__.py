def remove_root(data):
    if isinstance(data, dict) and len(data) == 1:
        first_value = list(data.values())[0]
        if isinstance(first_value, (dict, list)):
            return first_value
    return data
