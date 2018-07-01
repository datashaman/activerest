#!/usr/bin/env python
# -*- coding: utf-8 -*-

from activerest import Resource


class Todo(Resource):
    completed = False

    class Meta:
        site = 'https://jsonplaceholder.typicode.com/todos'


if __name__ == '__main__':
    if False:
        todos = Todo.all()
        print(todos)

        todos = Todo.find(params={'title_like': 'numquam'})
        print(todos)

        todo = Todo.find(id=1)
        print(todo)

        todo = Todo(title='new title')
        todo.save()
        print(todo)

        todo = Todo.find(1)
        todo.title = 'Blah'
        todo.save()
        print(todo)

        todo = Todo.find(1)
        todo.destroy()
        print(todo.is_persisted())

    print(Todo.delete(1))
