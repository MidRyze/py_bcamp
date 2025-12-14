import sqlite3
import os
from functools import wraps
from typing import Any, Callable

class db_manager:
    def __init__(self, db_name = "The To-do.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self): # initialize db
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                           email TEXT UNIQUE NOT NULL,
                           name TEXT NOT NULL,
                           password TEXT NOT NULL,
                           age INTEGER,
                           oid INTEGER PRIMARY KEY AUTOINCREMENT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                           email TEXT NOT NULL,
                           task_number INTEGER,
                           title TEXT NOT NULL,
                           status BOOLEAN DEFAULT 0,
                           description TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (email) REFERENCES users(email)
                           PRIMARY KEY (email, task_number)
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
        
    def update_user(self, new_user_email, old_user_email, name, password, age): # updates user info
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                UPDATE users
                SET email = ?, name = ?, password = ?, age = ?
                WHERE email = ?
                ''', (new_user_email, name, password, age, old_user_email))
            return cursor.rowcount > 0
        
    def create_todo_list(self, email, title, description): # create new todo list for user
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT MAX (task_number)
                FROM todo 
                WHERE email = ?
                ''', (email,)) # after , is the MAX no.
            result = cursor.fetchone()
            next_number = (result[0] or 0) + 1

            cursor.execute('''
                INSERT INTO todo (email, task_number, description)
                VALUES (?, ?, ?, ?)
                ''', (email, next_number, title, description)) # << this part, column order matters refer to line 59
            connect.commit()
            return next_number
        
    def get_users_tasks(self, user_email, for_checking = 0): # gets all tasks
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            if for_checking > 0:
                cursor.execute('''
                    SELECT t.email, t.name, t.task_number, t.title, t.status, t.description, t.created_at
                    FROM todo t
                    WHERE t.email = ? AND t.task_number = ?
                    ORDER BY t.created_at DESC
                    ''', (user_email, for_checking))
                return cursor.fetchone()
            
            else:
                cursor.execute('''
                    SELECT t.email, t.name, t.task_number, t.title, t.status, t.description, t.created_at
                    FROM todo t
                    WHERE t.email = ?
                    ORDER BY t.created_at DESC
                    ''', (user_email))
                return cursor.fetchall()
        
    def update_task_status(self, user_email, task_number, status): # updates task status
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                UPDATE todo
                SET status = ?
                WHERE email = ? AND task_number = ?
                ''', (status, user_email, task_number))
            return cursor.rowcount > 0
        
    def delete_task(self, user_email, task_number): # deletes a task
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                DELETE FROM todo
                WHERE email = ? AND task_number = ?
                ''', (user_email, task_number))
            return cursor.rowcount > 0

    def delete_user(self, user_email): # deletes a user
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM todo WHERE email = ?",(user_email))
            cursor.execute("DELETE FROM users WHERE email = ?",(user_email))
            return cursor.rowcount > 0

    def get_all_users(self): # gets all users *Admin only
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT * FROM users
                ''')
            return cursor.fetchall()
                
# choices: dict[str:init_db] = {"Create User":create_user,
#                           "Update User":,
#                           "Create Task":,
#                           "Read all Tasks":,
#                           "Update Task":,
#                           "Delete Task":,
#                           "Delete User":,
#                           "Read all Users":,
#                           }
def display_menu(): # Displays the menu in terminal
    print("\n" + "="*40)
    print("       DATABASE MANAGER")
    print("="*40)
    print("1 CREATE USER")
    print("2 CREATE NEW TASK")
    print("3 UPDATE TASK")
    print("4 VIEW TASK(S)")
    print("5 DELETE TASK")
    print("6 DELETE USER")
    # print("0 VIEW ALL USERS - ADMIN")
    print("C to Toggle 'Clear the terminal'")
    print("X to EXIT")
    print("="*40) 

def num_check(*args):
    inpt = []
    for i in args:
        try:
            inpt.append(int(i))
        except:
            print("Invalid entry, must be number")
            # raise SystemExit
            return None
    return inpt

def clear_terminal(x = 1):
    if x == 0:
        pass
        # return
    if os.name == 'nt':
        os.system('cls')  # Windows command to clear the terminal
        # return None
    else:
        os.system('clear')  # Unix-based command (Linux/macOS) to clear the terminal
        # return None
def main():
    clear_term = 1
    db = db_manager()

    while True:
        clear_terminal(clear_term)
        display_menu()
        choice = input("Please enter the the number of displayed options, type 'X' to exit.").strip().lower()
            
        if choice == 'c':
            if clear_term == 1:
                clear_term = 0
                print(f"Clear terminal was set to 1, now set to {clear_term}")
            else:
                clear_term = 1
                print(f"Clear terminal was set to 0, now set to {clear_term}")

        elif choice == '1':
            print("\n --- Create New User --- ")
            email = input("Enter e-mail: ").strip()
            name = input("Enter name: ").strip()
            password = input("Enter password: ").strip()
            age = input("Enter age (optional): ").strip()
            if age != "":
                age = num_check(input("Enter age: ").strip())
            try:
                if db.get_users_tasks(email):
                    print("Existing user, create Failed")
            except:
                user_id = db.create_user(name, email, password, age)
                print(f"/ User created successfully! ID: {user_id}")

        elif choice == '0':
            print("\n --- Get All Users --- ")            
            # email = input("Enter e-mail: ").strip()
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if username == "@!" and password == "":
                users = db.get_all_users()
                if users:
                    for u in users:
                        print(f"Obj_ID: {u[4]} | E-mail: {u[0]} | Name: {u[1]} | Age: {u[3]} | Time created: {u[5]}")

                else:
                    print("No users found.")

        elif choice == '2':
            print("\n --- Create New Task --- ")
            email = input("Enter e-mail: ").strip()
            title = input("Enter task: ").strip()
            description = input("Enter remarks for said task: ").strip()
            task = db.create_todo_list(email, title, description)
            if task:
                print(f"✓ Post created successfully! ID: {task}")
            else:
                print("✗ Failed to create post")

        elif choice == '3':
            print("\n --- Update Task --- ")
            email = input("Enter e-mail: ").strip()
            number = input("Please input task number: ").strip()
            status = input("Update status to (In-progress = 0, Done = 1): ").strip()
            number, status = num_check(number, status)
            task = db.update_task_status(email, number, status)
            if task:
                for t in task:
                    print(f"\nPost ID: {t['_id']}")
                    print(f"Title: {t['title']}")
                    print(f"Content: {t['content']}")
                    print(f"Created: {t['created_at']}")
                    print("-" * 30)
            else:
                print("No posts found for this user.")

        elif choice == '4':
            print("\n --- View Task(s) --- ")
            email = input("Enter e-mail: ").strip()
            all_tasks = db.get_users_tasks(email)
            if not all_tasks:
                print("Tasks list is empty.")
            view_all = input("Do you wish to view all tasks? (Y/N): ").strip().lower()
            if view_all =="y" and all_tasks:
                email_printed = False
                for t in all_tasks:
                    if email_printed == False:
                        print(f"\nE-mail: {t['email']}")
                        email_printed = True
                    print(f"\n#: {t['task_number']}")
                    print(f"Title: {t['title']}")
                    print(f"Status: {t['status']}")
                    print(f"Description: {t['description']}")
                    print(f"Created: {t['created_at']}")
                    print("-" * 30)
            else:
                number = num_check(input("Please input task number: ").strip())
                one_task = db.get_users_tasks(email, number)
                if not one_task:
                    print("Task number does not exist.")
                print(f"\nE-mail: {one_task['email']}")
                print(f"\n#: {one_task['task_number']}")
                print(f"Title: {one_task['title']}")
                print(f"Status: {one_task['status']}")
                print(f"Description: {one_task['description']}")
                print(f"Created: {one_task['created_at']}")
                print("-" * 30)

        elif choice == '5':
            print("\n --- Delete Task --- ")
            email = input("Enter e-mail: ").strip()
            number = num_check(input("Enter task number: ").strip())
            the_task = db.get_users_tasks(email, number)
            if not the_task:
                print("✗ User/Task not found for deletion.")
            confirm = input(f"Task no.{number}: {the_task}\nAre you sure you want to delete it? (Y/N): ").strip().lower()
            if confirm == 'y':
                db.delete_task(email, number)
                print("✓ Task deleted successfully!")
            else:
                print("Task deletion cancelled.")

        elif choice == '6':
            print("\n --- Delete User --- ")
            email = input("Enter e-mail to delete: ").strip()
            confirm = input(f"Are you sure you want to delete user {email}? (y/N): ").strip().lower()
            if confirm == 'y':
                if db.delete_user(email):
                    print("✓ User deleted successfully!")
                else:
                    print("✗ User not found or deletion failed.")

            else:
                print("Deletion cancelled.")

        elif choice == 'x':
            print("\nClosing database connection ... ")
            try:
                db.close_connection()
                print("Goodbye!")
                break
            except:
                print("Goodbye!")
                break


        else:
            print("✗ Invalid choice. Please enter the given options.")

        input("\nProses completed, press Enter to continue ... ")

def test():
    db = db_manager()

    while True:
        choice = input().strip()

        def num_check(*args):
            inpt = []
            for i in args:
                try:
                    inpt.append(int(i))
                except:
                    print("Invalid entry, must be number")
                    raise SystemExit
                    
            return inpt
        
        if choice == '1':
            print("\n --- Create New User --- ")
            email = input("Enter e-mail: ").strip()
            name = input("Enter name: ").strip()
            password = input("Enter password: ").strip()
            age = input("Enter age (optional): ").strip()
            if age != "":
                age = num_check(input("Enter age: ").strip())
            try:
                if db.get_users_tasks(email):
                    return "Existing user, create Failed"
            except:
                user_id = db.create_user(name, email, password, age)
                return f"/ User created successfully! ID: {user_id}"

# main()
if __name__ == "__main__":
    main()
    # test()
    pass