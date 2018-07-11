from unittest import TestCase

from activerest.formats import json_format


class JsonFormatTest(TestCase):
    def test_extension(self):
        self.assertEqual('json', json_format.extension())

    def test_mime_type(self):
        self.assertEqual('application/json', json_format.mime_type())

    def test_encode(self):
        data = {"values": [1, 2]}
        expected = '{"values": [1, 2]}'
        self.assertEqual(expected, json_format.encode(data, indent=None))

    def test_decode(self):
        text = '{"values":[1,2],"other_value":2}'
        expected = {"values": [1, 2], "other_value": 2}
        self.assertEqual(expected, json_format.decode(text))

    def test_decode_with_single_list(self):
        text = '{"values":[1,2]}'
        expected = [1, 2]
        self.assertEqual(expected, json_format.decode(text))

    def test_decode_with_single_dict(self):
        text = '{"values":{"attr":"value"}}'
        expected = {"attr": "value"}
        self.assertEqual(expected, json_format.decode(text))
