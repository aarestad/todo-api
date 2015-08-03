import unittest
import todo_api
import sqlite3
import json

todo_api.DATABASE = './todo_test.db'


class TodoApiTest(unittest.TestCase):
    def setUp(self):
        self.app = todo_api.app.test_client()

        self.db = sqlite3.connect(todo_api.DATABASE)
        self.c = self.db.cursor()

        self.db.execute('DROP TABLE IF EXISTS todo_items')

        with open('todo_schema.sql') as schema:
            script = schema.read()
            self.db.executescript(script)
            self.db.commit()

    def test_save_todo_item(self):
        self.assertEqual(0, self.c.execute('select count(*) from todo_items').fetchone()[0])

        new_todo_item = todo_api.TodoItem('peter', 'Get the milk', 1234567890)

        new_todo_item = todo_api.save_todo_item(new_todo_item, self.db)

        self.assertEqual(('peter', 'Get the milk', 1234567890, new_todo_item.id, False),
                         self.c.execute('SELECT username, description, due_date, id, completed '
                                        'FROM todo_items WHERE id = ?', (new_todo_item.id,)).fetchone())

    def test_find_todo_item_by_id(self):
        new_todo_item = todo_api.TodoItem('peter', 'Get the milk', 1234567890)
        todo_api.save_todo_item(new_todo_item, self.db)

        fetched_todo_item = todo_api.find_todo_item_by_id(new_todo_item.id, self.db)

        self.assertEqual(new_todo_item.id, fetched_todo_item.id)
        self.assertEqual(new_todo_item.username, fetched_todo_item.username)
        self.assertEqual(new_todo_item.description, fetched_todo_item.description)
        self.assertEqual(new_todo_item.due_date, fetched_todo_item.due_date)
        self.assertEqual(new_todo_item.completed, fetched_todo_item.completed)

    def test_find_todo_items_by_username(self):
        new_todo_item_1 = todo_api.TodoItem('peter', 'Get the milk', 1234567890, None, True)
        new_todo_item_2 = todo_api.TodoItem('peter', 'Get the bread', 1234567890, None, False)
        todo_api.save_todo_item(new_todo_item_1, self.db)
        todo_api.save_todo_item(new_todo_item_2, self.db)

        all_by_username = todo_api.find_todo_items_by_username('peter', self.db)
        self.assertEqual(2, len(all_by_username))

        uncompleted_by_username = todo_api.find_todo_items_by_username('peter', self.db, True)
        self.assertEqual(1, len(uncompleted_by_username))

        uncompleted = uncompleted_by_username[0]
        self.assertEqual(uncompleted.username, 'peter')
        self.assertEqual(uncompleted.description, 'Get the bread')
        self.assertEqual(uncompleted.due_date, 1234567890)
        self.assertEqual(uncompleted.completed, False)

    def test_todos_for_user_flask(self):
        new_todo_item_1 = todo_api.TodoItem('peter', 'Get the milk', 1234567890, None, True)
        new_todo_item_2 = todo_api.TodoItem('peter', 'Get the bread', 1234567890, None, False)
        todo_api.save_todo_item(new_todo_item_1, self.db)
        todo_api.save_todo_item(new_todo_item_2, self.db)

        json_response = self.app.get('/todo-api/v1/todos/peter/').data
        todos = json.loads(json_response)['todo_items']
        self.assertEqual(2, len(todos))

    def test_uncompleted_todos_for_user_flask(self):
        new_todo_item_1 = todo_api.TodoItem('peter', 'Get the milk', 1234567890, None, True)
        new_todo_item_2 = todo_api.TodoItem('peter', 'Get the bread', 1234567890, None, False)
        todo_api.save_todo_item(new_todo_item_1, self.db)
        todo_api.save_todo_item(new_todo_item_2, self.db)

        json_response = self.app.get('/todo-api/v1/todos/peter/uncompleted').data
        todos = json.loads(json_response)['uncompleted_todo_items']
        self.assertEqual(1, len(todos))

    def test_save_new_todo_flask(self):
        new_todo = {'username': 'peter', 'description': 'Get the milk', 'due_date': 1438776000}
        response = self.app.post('/todo-api/v1/todo/', data=json.dumps(new_todo), content_type='application/json')

        new_todo_response = json.loads(response.data)
        self.assertEqual(False, new_todo_response['completed'])
        self.assertEqual('Get the milk', new_todo_response['description'])
        self.assertEqual(1438776000, new_todo_response['due_date'])
        self.assertEqual('peter', new_todo_response['username'])
        self.assertEqual(1, new_todo_response['id'])

    def todo_item_complete_flask(self):
        todo_item = todo_api.TodoItem('peter', 'Get the bread', 1234567890, None, False)
        todo_item = todo_api.save_todo_item(todo_item, self.db)

        response = self.app.post('/todo-api/v1/todo/' + todo_item.id + '/complete')

        todo_response = json.loads(response.data)
        self.assertEqual(True, todo_response['completed'])
        self.assertEqual('Get the milk', todo_response['description'])
        self.assertEqual(1234567890, todo_response['due_date'])
        self.assertEqual('peter', todo_response['username'])
        self.assertEqual(todo_item.id, todo_response['id'])


if __name__ == '__main__':
    unittest.main()
