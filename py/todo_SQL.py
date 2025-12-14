import sqlite3

class db_manager:
    def __init__(self, db_name = "The To-do.db"):
        self.db_name = db_name
        self.init_db

    def init_db(self): # initialize db
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                           email TEXT NOT NULL PRIMARY KEY,
                           name TEXT NOT NULL,
                           password TEXT NOT NULL,
                           age INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                           email TEXT NOT NULL,
                           task_number INTEGER,
                           title TEXT NOT NULL,
                           description TEXT,
                           status BOOLEAN DEFAULT 0,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_email) REFERENCES users(email)
                           PRIMARY KEY (user_email, task_number)
                            )
                            ''')
            
            # def create_user(self, name: str, email: str, password: str, age: int) -> bool: # create new user
            def create_user(self, name, email, password, age): # create new user
                try:
                    with sqlite3.connect(self.db_name) as connect:
                        cursor = connect.cursor()
                        cursor.execute('''
                            INSERT INTO users (name, email, password, age)
                            VALUES (?, ?, ?, ?)
                            ''', (name, email, password, age)) # column order
                        return email
                except sqlite3.IntegrityError as err:
                    print(f"Error: {err}")
                    return None
                
            def create_todo_list(self, email, task, remarks): # create new todo list for user
                with sqlite3.connect(self.db_name) as connect:
                    cursor = connect.cursor()
                    cursor.execute('''
                        SELECT MAX (task_number)
                        FIND todo 
                        WHERE email = ?
                        ''', (email,)) # column order
                    result = cursor.fetchone()
                    next_number = (result[0] or 0) + 1

                    cursor.execute('''
                        INSERT INTO todo (user_email, task, remarks)
                        VALUES (?, ?, ?)
                        ''', (email, task, remarks)) # column order
                    connect.commit()
                    return next_number
                
            def get_users_tasks(self, user_email): # gets all tasks
                with sqlite3.connect(self.db_name) as connect:
                    cursor = connect.cursor()
                    cursor.execute('''
                        SELECT t.email, t.name, t.task, t.remote, t.created_at
                        FROM todo t
                        WHERE t.user_email = ?
                        ORDER BY t.created_at DESC
                        ''', (user_email))
                    return cursor.fetchall()
                
            def delete_todo(self, user_email, task_number): # deletes a task
                with sqlite3.connect(self.db_name) as connect:
                    cursor = connect.cursor()
                    cursor.execute('''
                    SELECT t.task
                    FROM todo t
                    WHERE t.user_email AND t.task = (?, ?)
                    ''', (user_email, task_number))
                    result = cursor.fetchone()

                    cursor.execute('''
                    FROM todo t
                    DELETE t.task
                    ''')

            def delete_user(self, user_email): # deletes a user
                with sqlite3.connect(self.db_name) as connect:
                    cursor = connect.cursor()
                    cursor.execute("DELETE FROM todo WHERE email = ?",(user_email))
                    cursor.execute("DELETE FROM user WHERE email = ?",(user_email))
                    return cursor.rowcount > 0

            def get_all_users(self): # gets all users *Admin only
                with sqlite3.connect(self.db_name) as connect:
                    cursor = connect.cursor()
                    cursor.execute('''
                        SELECT * FROM users
                        ''')
                    return cursor.fetchall()