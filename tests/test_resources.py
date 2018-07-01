import requests_mock

from activerest import Resource
from unittest import TestCase


class Todo(Resource):
    completed: False

    class Meta:
        site = 'http://example.com/todos'


@requests_mock.Mocker()
class TestResources(TestCase):
    def assert_todo_list(self, expected, actual):
        assert list == type(actual)
        assert len(expected) == len(actual)

        for index, expected_todo in enumerate(expected):
            actual_todo = actual[index]

            assert type(actual_todo) == Todo

            for k, v in expected_todo.items():
                assert v == getattr(actual_todo, k)

    def assert_todo(self, expected, actual):
        assert type(actual) == Todo

        for k, v in expected.items():
            assert v == getattr(actual, k)

    def test_all(self, m):
        expected = [
            {'id': 1, 'title': 'still todo', 'completed': False},
            {'id': 2, 'title': 'done', 'completed': True},
        ]

        m.register_uri(
            'GET',
            'http://example.com/todos',
            json=expected,
            status_code=200
        )

        actual = Todo.find()
        self.assert_todo_list(expected, actual)

    def test_find_by_id(self, m):
        expected = {'id': 1, 'title': 'still todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=200
        )

        actual = Todo.find(1)
        self.assert_todo(expected, actual)

    def test_find_by_params(self, m):
        expected = [
            {'id': 1, 'title': 'still todo', 'completed': False},
        ]

        m.register_uri(
            'GET',
            'http://example.com/todos?title=still+todo',
            json=expected,
            status_code=200
        )

        actual = Todo.find(params={'title': 'still todo'})
        self.assert_todo_list(expected, actual)
