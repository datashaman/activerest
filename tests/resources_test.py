import requests_mock

from activerest import Resource
from unittest import TestCase


class Todo(Resource):
    completed = False

    class Meta:
        site = 'http://example.com/todos'


@requests_mock.Mocker()
class ResourcesTest(TestCase):
    def assert_todo_list(self, expected, actual):
        self.assertIsInstance(actual, list)
        self.assertEqual(len(expected), len(actual))

        for index, expected_todo in enumerate(expected):
            actual_todo = actual[index]
            self.assertIsInstance(actual_todo, Todo)
            self.assertEqual(expected_todo, actual_todo.attributes)

    def assert_todo(self, expected, actual):
        self.assertIsInstance(actual, Todo)
        self.assertEqual(expected, actual.attributes)

    def test_find_all(self, m):
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

        actual = Todo.all()

        self.assert_todo_list(expected, actual)

    def test_delete(self, m):
        m.register_uri(
            'DELETE',
            'http://example.com/todos/1',
            status_code=200
        )

        self.assertTrue(Todo.delete(1))

    def test_does_exist(self, m):
        m.register_uri(
            'HEAD',
            'http://example.com/todos/1',
            status_code=200
        )

        self.assertTrue(Todo.exists(1))

    def test_does_not_exist(self, m):
        m.register_uri(
            'HEAD',
            'http://example.com/todos/1',
            status_code=404
        )

        self.assertFalse(Todo.exists(1))

    def test_destroy(self, m):
        expected = {'id': 1, 'title': 'still todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=200
        )

        m.register_uri(
            'DELETE',
            'http://example.com/todos/1',
            status_code=200
        )

        todo = Todo.find(1)
        self.assertTrue(todo.destroy())

    def test_create(self, m):
        attributes = {'title': 'new todo'}
        expected = {'id': 1, 'completed': False}
        expected.update(attributes)

        m.register_uri(
            'POST',
            'http://example.com/todos',
            json=expected,
            status_code=201
        )

        todo = Todo(**attributes)
        todo.save()

        self.assertTrue(todo.is_persisted())
        self.assert_todo(expected, todo)

    def test_update(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}
        changes = {'title': 'amended todo', 'completed': True}
        amended = {'id': 1}
        amended.update(changes)

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=200
        )

        m.register_uri(
            'PUT',
            'http://example.com/todos/1',
            json=amended,
            status_code=200
        )

        todo = Todo.find(1)
        for k, v in changes.items():
            setattr(todo, k, v)
        todo.save()

        self.assertTrue(todo.is_persisted())
        self.assert_todo(amended, todo)
