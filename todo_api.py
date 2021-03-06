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


class TodoItem(object):
    def __init__(self, username, description, due_date, item_id=None, completed=False):
        self.id = item_id
        self.username = username
        self.description = description
        self.due_date = due_date
        self.completed = bool(completed)


def save_todo_item(todo_item, db):
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


def find_todo_item_by_id(todo_item_id, db):
    cursor = db.cursor()

    cursor.execute('SELECT username, description, due_date, id, completed FROM todo_items where id = ?',
                   (todo_item_id,))

    todo_item_row = cursor.fetchone()

    return None if todo_item_row is None else TodoItem(*todo_item_row)


def find_todo_items_by_username(username, db, only_incomplete=False):
    cursor = db.cursor()

    query = 'SELECT username, description, due_date, id, completed FROM todo_items where username = ?'

    if only_incomplete:
        query += ' AND completed = 0'

    return [TodoItem(*todo_item_row) for todo_item_row in cursor.execute(query, (username,))]


@app.route('/todo-api/v1/todo/', methods=['POST'])
def new_todo():
    try:
        new_todo_item = TodoItem(**request.json)
    except TypeError:
        return 'Invalid todo object', 400

    new_todo_item = save_todo_item(new_todo_item, get_db())
    return json.jsonify(new_todo_item.__dict__), 201


@app.route('/todo-api/v1/todo/<todo_id>/complete', methods=['POST'])
def todo_item_complete(todo_id):
    existing_todo_item = find_todo_item_by_id(todo_id, get_db())

    if existing_todo_item is None:
        return 'Todo item %s not found' % (todo_id,), 404

    existing_todo_item.completed = True
    save_todo_item(existing_todo_item, get_db())
    return json.jsonify(existing_todo_item.__dict__)


@app.route('/todo-api/v1/todos/<username>/')
def todos_for_user(username):
    todo_items = [todo_item.__dict__ for todo_item in find_todo_items_by_username(username, get_db())]

    if len(todo_items) == 0:
        return 'No todo items found for %s' % (username,), 404

    return json.jsonify({"todo_items": todo_items})


@app.route('/todo-api/v1/todos/<username>/uncompleted')
def uncompleted_todos_for_user(username):
    uncompleted_todo_items = [todo_item.__dict__ for todo_item in find_todo_items_by_username(username, get_db(), True)]

    if len(uncompleted_todo_items) == 0:
        return 'No uncompleted todo items found for %s' % (username,), 404

    return json.jsonify({"uncompleted_todo_items": uncompleted_todo_items})


if __name__ == '__main__':
    app.run()
