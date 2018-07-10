def remove_root(data):
    if isinstance(data, dict) and len(data) == 1:
        data = list(data.values())[0]
        if isinstance(data, list):
            return data
    else:
        return data
