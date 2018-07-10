def remove_root(data):
    if isinstance(data, dict) and len(data) == 1 and isinstance(data.items()[0], list):
        return data.items()[0]
    else:
        return data
