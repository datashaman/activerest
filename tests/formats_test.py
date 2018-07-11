from activerest.formats import remove_root
from unittest import TestCase


class FormatsTest(TestCase):
    def test_remove_root_with_single_list(self):
        values = [{'attr': 'value'}]
        data = {'values': values}
        self.assertEqual(values, remove_root(data))

    def test_remove_root_with_single_dict(self):
        value = {'attr': 'value'}
        data = {'value': value}
        self.assertEqual(value, remove_root(data))

    def test_remove_root_with_multiple_root(self):
        data = {'values': {}, 'other': {}}
        self.assertEqual(data, remove_root(data))
