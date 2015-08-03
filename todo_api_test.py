import unittest

import todo_api

import sqlite3

todo_api.DATABASE = './todo_test.db'


class TodoApiTest(unittest.TestCase):
    def setUp(self):
        db = sqlite3.connect(todo_api.DATABASE)

        db.execute('DROP TABLE IF EXISTS todo_items')

        with open('todo_schema.sql') as schema:
            script = schema.read()
            db.executescript(script)
            db.commit()

    def test_save_todo_item(self):
        db = sqlite3.connect(todo_api.DATABASE)
        c = db.cursor()

        self.assertEqual(0, c.execute('select count(*) from todo_items').fetchone()[0])

        new_todo_item = todo_api.TodoItem('peter', 'Get the milk', 1234567890)

        new_todo_item = todo_api.save_todo_item(new_todo_item, db)

        self.assertEqual(('peter', 'Get the milk', 1234567890, new_todo_item.id, False),
                         c.execute('SELECT username, description, due_date, id, completed '
                                   'FROM todo_items WHERE id = ?', (new_todo_item.id,)).fetchone())

    def find_todo_item_by_id(self):
        db = sqlite3.connect(todo_api.DATABASE)

        new_todo_item = todo_api.TodoItem('peter', 'Get the milk', 1234567890)
        todo_api.save_todo_item(new_todo_item, db)

        fetched_todo_item = todo_api.find_todo_item_by_id(new_todo_item.id)

        self.assertEqual(new_todo_item.id, fetched_todo_item.id)
        self.assertEqual(new_todo_item.username, fetched_todo_item.username)
        self.assertEqual(new_todo_item.description, fetched_todo_item.description)
        self.assertEqual(new_todo_item.due_date, fetched_todo_item.due_date)
        self.assertEqual(new_todo_item.completed, fetched_todo_item.completed)

    def test_find_todo_items_by_username(self):
        db = sqlite3.connect(todo_api.DATABASE)

        new_todo_item_1 = todo_api.TodoItem('peter', 'Get the milk', 1234567890, None, True)
        new_todo_item_2 = todo_api.TodoItem('peter', 'Get the bread', 1234567890, None, False)
        todo_api.save_todo_item(new_todo_item_1, db)
        todo_api.save_todo_item(new_todo_item_2, db)

        all_by_username = todo_api.find_todo_items_by_username('peter', db)
        self.assertEqual(2, len(all_by_username))

        uncompleted_by_username = todo_api.find_todo_items_by_username('peter', db, True)
        self.assertEqual(1, len(uncompleted_by_username))

        uncompleted = uncompleted_by_username[0]
        self.assertEqual(uncompleted.username, 'peter')
        self.assertEqual(uncompleted.description, 'Get the bread')
        self.assertEqual(uncompleted.due_date, 1234567890)
        self.assertEqual(uncompleted.completed, False)
