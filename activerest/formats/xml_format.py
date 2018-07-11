import xmltodict

from activerest.formats import remove_root


def extension():
    return 'xml'

def mime_type():
    return 'application/xml'

def encode(data, **kwargs):
    if 'full_document' not in kwargs:
        kwargs['full_document'] = False

    if 'pretty' not in kwargs:
        kwargs['pretty'] = True

    return xmltodict.unparse(data, **kwargs)

def decode(text):
    return remove_root(xmltodict.parse(text))
