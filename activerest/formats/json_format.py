import json

from activerest.formats import remove_root


def extension():
    return 'json'

def mime_type():
    return 'application/json'

def encode(data, **kwargs):
    encode_kwargs = {
        'indent': 4,
    }
    encode_kwargs.update(kwargs)
    return json.dumps(data, **encode_kwargs)

def decode(text):
    return remove_root(json.loads(text))
