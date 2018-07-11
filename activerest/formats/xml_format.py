import xmltodict

from activerest.formats import remove_root


def extension():
    return 'xml'

def mime_type():
    return 'application/xml'

def encode(data, **kwargs):
    encode_kwargs = {
        'full_document': False,
        'pretty': True,
    }
    encode_kwargs.update(kwargs)
    return xmltodict.unparse(data, **encode_kwargs)

def decode(text):
    return remove_root(xmltodict.parse(text))
