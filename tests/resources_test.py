from future.utils import viewitems

import base64
import requests
import requests_mock
import six

from activerest import Connection, Resource
from furl import furl
from requests.exceptions import HTTPError
from unittest import TestCase

class ExampleConnection(Connection):
    pass


class Todo(Resource):
    site = 'http://example.com'


class TodoWithElementName(Resource):
    site = 'http://example.com'
    element_name = 'horse'


class TodoWithBasicAuth(Resource):
    site = 'http://example.com'
    element_name = 'todo'
    auth_type = 'basic'
    username = 'user'
    password = 'password'


class TodoWithBasicAuthInSite(Resource):
    site = 'http://user:password@example.com'
    element_name = 'todo'
    auth_type = 'basic'


class TodoWithDigestAuth(Resource):
    site = 'http://example.com'
    element_name = 'todo'
    auth_type = 'digest'
    username = 'user'
    password = 'password'


class TodoWithTimeout(Resource):
    site = 'http://example.com'
    element_name = 'todo'
    timeout = 60


class TodoWithConnectionClass(Resource):
    site = 'http://example.com'
    connection_class = ExampleConnection

    auth_type = 'basic'
    open_timeout = 3
    password = 'password'
    proxies = {
        'http': 'http://proxy.example.com',
        'https': 'https://proxy.example.com',
    }
    read_timeout = 27
    timeout = 12
    username = 'username'


class TodoWithoutSite(Resource):
    pass


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
            status_code=requests.codes.ok
        )

        actual = Todo.find()
        self.assert_todo_list(expected, actual)

    def test_find_by_id(self, m):
        expected = {'id': 1, 'title': 'still todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=requests.codes.ok
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
            status_code=requests.codes.ok
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
            status_code=requests.codes.ok
        )

        actual = Todo.all()

        self.assert_todo_list(expected, actual)

    def test_delete(self, m):
        m.register_uri(
            'DELETE',
            'http://example.com/todos/1',
            status_code=requests.codes.ok
        )

        self.assertTrue(Todo.delete(1))

    def test_does_exist(self, m):
        m.register_uri(
            'HEAD',
            'http://example.com/todos/1',
            status_code=requests.codes.ok
        )

        self.assertTrue(Todo.exists(1))

    def test_does_not_exist(self, m):
        m.register_uri(
            'HEAD',
            'http://example.com/todos/1',
            status_code=requests.codes.not_found
        )

        self.assertFalse(Todo.exists(1))

    def test_destroy(self, m):
        expected = {'id': 1, 'title': 'still todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=requests.codes.ok
        )

        m.register_uri(
            'DELETE',
            'http://example.com/todos/1',
            status_code=requests.codes.ok
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
            status_code=requests.codes.created
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
            status_code=requests.codes.ok
        )

        m.register_uri(
            'PUT',
            'http://example.com/todos/1',
            json=amended,
            status_code=requests.codes.ok
        )

        todo = Todo.find(1)
        for (key, value) in viewitems(changes):
            setattr(todo, key, value)
        todo.save()

        self.assertTrue(todo.is_persisted())
        self.assert_todo(amended, todo)

    def test_element_name(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/horses/1',
            json=expected,
            status_code=requests.codes.ok
        )

        actual = TodoWithElementName.find(1)
        self.assertEqual(expected, actual.attributes)

    def test_digest_auth(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=requests.codes.ok
        )

        actual = TodoWithDigestAuth.find(1)
        self.assertEqual(expected, actual.attributes)

    def test_basic_auth(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}

        request_headers = {
            'Authorization': requests.auth._basic_auth_str('user', 'password'),
        }

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            request_headers=request_headers,
            json=expected,
            status_code=requests.codes.ok
        )

        actual = TodoWithBasicAuth.find(1)
        self.assertEqual(expected, actual.attributes)

    def test_basic_auth_in_site(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}

        request_headers = {
            'Authorization': requests.auth._basic_auth_str('user', 'password'),
        }

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            request_headers=request_headers,
            json=expected,
            status_code=requests.codes.ok
        )

        actual = TodoWithBasicAuthInSite.find(1)
        self.assertEqual(expected, actual.attributes)

    def test_repr(self, m):
        if six.PY2:
            expected = "Todo(completed=False, id=1, title='new todo')"
        else:
            expected = "Todo(id=1, title='new todo', completed=False)"

        todo = Todo(id=1, title='new todo', completed=False)
        self.assertEqual(expected, str(todo))

    def test_update_attribute(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}
        updated = {'id': 1, 'title': 'new title', 'completed': False}

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=requests.codes.ok
        )

        m.register_uri(
            'PUT',
            'http://example.com/todos/1',
            json=updated,
            status_code=requests.codes.ok
        )

        actual = Todo.find(1)
        actual.update_attribute('title', 'new title')
        self.assertEqual(updated, actual.attributes)

    def test_update_attributes(self, m):
        expected = {'id': 1, 'title': 'new todo', 'completed': False}
        updates = {
            'title': 'new title',
            'completed': True,
        }
        updated = {'id': 1}
        updated.update(updates)

        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            json=expected,
            status_code=requests.codes.ok
        )

        m.register_uri(
            'PUT',
            'http://example.com/todos/1',
            json=updated,
            status_code=requests.codes.ok
        )

        actual = Todo.find(1)
        actual.update_attributes(updates)
        self.assertEqual(updated, actual.attributes)

    def test_destroy_new(self, m):
        todo = Todo(title='new todo')
        self.assertFalse(todo.destroy())

    def test_find_by_params_with_no_results(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos',
            json=[],
            status_code=requests.codes.ok
        )

        self.assertEqual([], Todo.find())

    def test_timeout(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos',
            json=[],
            status_code=requests.codes.ok
        )

        self.assertEqual([], TodoWithTimeout.find())

    def test_connection_class(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos',
            json=[],
            status_code=requests.codes.ok
        )

        connection = TodoWithConnectionClass.connection()

        self.assertIsInstance(connection, ExampleConnection)

        self.assertEqual(furl(TodoWithConnectionClass.site), connection.site)

        self.assertEqual(TodoWithConnectionClass.auth_type, connection.auth_type)
        self.assertEqual(TodoWithConnectionClass.open_timeout, connection.open_timeout)
        self.assertEqual(TodoWithConnectionClass.password, connection.password)
        self.assertEqual(TodoWithConnectionClass.proxies, connection.proxies)
        self.assertEqual(TodoWithConnectionClass.read_timeout, connection.read_timeout)
        self.assertEqual(TodoWithConnectionClass.timeout, connection.timeout)
        self.assertEqual(TodoWithConnectionClass.username, connection.username)

    def test_without_site(self, m):
        with self.assertRaises(ValueError, msg='resource must have site defined'):
            todo = TodoWithoutSite()

    def test_save_error(self, m):
        m.register_uri(
            'POST',
            'http://example.com/todos',
            status_code=500
        )

        todo = Todo()
        self.assertFalse(todo.save())

    def test_not_found(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            status_code=404
        )

        todo = Todo.find(1)
        self.assertIsNone(todo)

    def test_find_single_exception(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos/1',
            status_code=500
        )

        with self.assertRaises(HTTPError):
            Todo.find(1)

    def test_find_collection_exception(self, m):
        m.register_uri(
            'GET',
            'http://example.com/todos',
            status_code=500
        )

        with self.assertRaises(HTTPError):
            Todo.find()
