import xmxltodict

from activerest.formats import remove_root


def extension():
    return 'xml'

def mime_type():
    return 'application/xml'

def encode(data, **kwargs):
    return xmltodict.unparse(data, pretty=True)

def decode(text):
    return remove_root(xmltodict.parse(text))
