CREATE TABLE todo_items (
  id INTEGER PRIMARY KEY,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  username VARCHAR(255) NOT NULL,
  due_date DATETIME NOT NULL
);
