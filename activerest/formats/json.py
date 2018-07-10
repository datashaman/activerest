import json

from activerest.formats import remove_root


def extension():
    return 'json'

def mime_type():
    return 'application/json'

def encode(data, **kwargs):
    return json.dumps(data, **kwargs)

def decode(text):
    return remove_root(json.loads(text))
