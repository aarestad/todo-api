# todo-api
A simple todo API based on Flask

# Requirements

- Python 2.7.x
- Flask (http://flask.pocoo.org/)

To install Flask:

    pip install Flask

To run from the command line:

    python todo_api.py

# API documentation

## Create a new to-do item

### API endpoint

    /todo-api/v1/todo/

Method: POST

### Expected JSON body

    {
      "username":"peter",
      "description":"Get the milk",
      "due_date": 1438776000 # Unix-style timestam
    }

### Response

    {
      "completed": false,
      "description": "Get the milk",
      "due_date": 1438776000,
      "id": 1,
      "username": "peter"
    }

HTTP status: 201

## Mark a to-do item as completed

### API endpoint

    /todo-api/v1/todo/<todo_id>/complete

Method: POST

No post body required. `<todo_id>` should be the ID of the to-do item you wish to mark as complete, previously returned
as the `id` field of the JSON response of a previously-created item

### Response

If the given ID is present in the database:

    {
      "completed": true,
      "description": "Get the milk",
      "due_date": 1438776000,
      "id": 3,
      "username": "peter"
    }

HTTP status: 200

If the given ID is not present in the database:

    Todo item 999 not found

HTTP status: 404

## Fetch to-do items for a user

### API endpoint

    /todo-api/v1/todos/<username>/

Method: GET

### Response

If at least one item is found for the user:

    {
      "todo_items": [
        {
          "completed": false,
          "description": "Get the milk",
          "due_date": 1438776000,
          "id": 1,
          "username": "peter"
        },
        {
          "completed": false,
          "description": "Get bread",
          "due_date": 1438776000,
          "id": 2,
          "username": "peter"
        },
        {
          "completed": true,
          "description": "Get pizza",
          "due_date": 1438776000,
          "id": 3,
          "username": "peter"
        },
        {
          "completed": false,
          "description": "Conquer the world",
          "due_date": 1438776000,
          "id": 4,
          "username": "peter"
        }
      ]
    }

HTTP status: 200

If no items are found for the user:

    No todo items found for joe

HTTP status: 404

## Fetch uncompleted to-do items for a user

### API endpoint

    /todo-api/v1/todos/<username>/uncompleted

Method: GET

### Response

If at least one uncompleted item is found for the user:

    {
      "uncompleted_todo_items": [
        {
          "completed": false,
          "description": "Get the milk",
          "due_date": 1438776000,
          "id": 1,
          "username": "peter"
        },
        {
          "completed": false,
          "description": "Get the milk",
          "due_date": 1438776000,
          "id": 2,
          "username": "peter"
        },
        {
          "completed": false,
          "description": "Get the milk",
          "due_date": 1438776000,
          "id": 4,
          "username": "peter"
        }
      ]
    }

HTTP status: 200

If no uncompleted items are found for the user:

    No uncompleted todo items found for joe

HTTP status: 404