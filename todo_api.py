#!/usr/bin/env python

from flask import Flask, request, json, g

import sqlite3

app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True

DATABASE = './todo.db'


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    return db


@app.teardown_appcontext
def close_connection(ex):
    db = getattr(g, '_database', None)

    if db is not None:
        db.close()


def save_todo_item(todo_item):
    db = get_db()
    cursor = db.cursor()

    if todo_item.id is None:
        cursor.execute('INSERT INTO todo_items (description, completed, username, due_date) VALUES (?, ?, ?, ?)',
                       (todo_item.description, todo_item.completed, todo_item.username, todo_item.due_date))
        todo_item.id = cursor.lastrowid
    else:
        cursor.execute('UPDATE todo_items '
                       'SET description = ?, completed = ?, username = ?, due_date = ? '
                       'WHERE id = ?',
                       (todo_item.description, todo_item.completed, todo_item.username,
                        todo_item.due_date, todo_item.id))

    db.commit()

    return todo_item


def find_todo_item_by_id(todo_item_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id, username, description, due_date, completed FROM todo_items where id = ?',
                   (todo_item_id,))

    todo_item_row = cursor.fetchone()

    if todo_item_row is None:
        return None

    return TodoItem(*todo_item_row)


def find_todo_items_by_username(username, only_incomplete=False):
    db = get_db()
    cursor = db.cursor()

    query = 'SELECT id, username, description, due_date, completed FROM todo_items where username = ?'

    if only_incomplete:
        query += ' AND completed = 0'

    cursor.execute(query, (username,))

    todo_items = []

    for todo_item_row in cursor:
        todo_items.append(TodoItem(*todo_item_row))

    return todo_items


class TodoItem(object):
    def __init__(self, item_id, username, description, due_date, completed):
        self.id = item_id
        self.username = username
        self.description = description
        self.due_date = due_date
        self.completed = bool(completed)

    def as_map(self):
        return {
            'id': self.id,
            'username': self.username,
            'description': self.description,
            'due_date': self.due_date,
            'completed': self.completed
        }

    @staticmethod
    def from_dict(todo_dict):
        return TodoItem(todo_dict.get('id', None), todo_dict['username'], todo_dict['description'],
                        todo_dict['due_date'], todo_dict.get('completed', False))


@app.route('/todo-api/v1/todo/', methods=['POST'])
def new_todo():
    new_todo_item = TodoItem.from_dict(request.json)
    new_todo_item = save_todo_item(new_todo_item)
    return json.jsonify(new_todo_item.as_map()), 201


@app.route('/todo-api/v1/todo/<todo_id>/complete', methods=['POST'])
def todo_item_complete(todo_id):
    existing_todo_item = find_todo_item_by_id(todo_id)

    if existing_todo_item is None:
        return 'Todo item %s not found' % (todo_id,), 404

    existing_todo_item.completed = True
    save_todo_item(existing_todo_item)
    return json.jsonify(existing_todo_item.as_map())


@app.route('/todo-api/v1/todos/<username>/')
def todos_for_user(username):
    todo_items = [todo_item.as_map() for todo_item in find_todo_items_by_username(username)]

    if len(todo_items) == 0:
        return 'No todo items found for %s' % (username,), 404

    return json.jsonify({"todo_items": todo_items})


@app.route('/todo-api/v1/todos/<username>/uncompleted')
def uncompleted_todos_for_user(username):
    uncompleted_todo_items = [todo_item.as_map() for todo_item in find_todo_items_by_username(username, True)]

    if len(uncompleted_todo_items) == 0:
        return 'No uncompleted todo items found for %s' % (username,), 404

    return json.jsonify({"uncompleted_todo_items": uncompleted_todo_items})


if __name__ == '__main__':
    app.run()
