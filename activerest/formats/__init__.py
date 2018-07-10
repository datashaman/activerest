def remove_root(data):
    if isinstance(data, dict) and len(data) == 1 and isinstance(list(data.values())[0], list):
        return list(data.values())[0]
    else:
        return data
