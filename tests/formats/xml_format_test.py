from unittest import TestCase

from activerest.formats import xml_format
from collections import OrderedDict


class XmlFormatTest(TestCase):
    def test_extension(self):
        self.assertEqual('xml', xml_format.extension())

    def test_mime_type(self):
        self.assertEqual('application/xml', xml_format.mime_type())

    def test_encode_with_dict(self):
        data = {"value": {"attr": "name"}}
        expected = '''<value>
	<attr>name</attr>
</value>'''
        self.assertEqual(expected, xml_format.encode(data))

    def test_encode_with_list(self):
        data = {"value": [1, 2]}
        expected = '<value>1</value><value>2</value>'
        self.assertEqual(expected, xml_format.encode(data))

    def test_decode(self):
        text = '''<?xml version="1.0"?>
        <root>
            <value>1</value>
            <value>2</value>
            <other_value>2</other_value>
        </root>
        '''
        expected = OrderedDict({'value': ['1', '2'], 'other_value': '2'})
        self.assertEqual(expected, xml_format.decode(text))

    def test_decode_with_single_list(self):
        text = '<root><value>1</value><value>2</value></root>'
        expected = OrderedDict({'value': ['1', '2']})
        self.assertEqual(expected, xml_format.decode(text))

    def test_decode_with_single_dict(self):
        text = '<value><attr>name</attr></value>'
        expected = OrderedDict({"attr": "name"})
        self.assertEqual(expected, xml_format.decode(text))
