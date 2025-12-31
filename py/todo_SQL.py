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
                           oid INTEGER PRIMARY KEY,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                           email TEXT NOT NULL,
                           task_number INTEGER,
                           title TEXT NOT NULL,
                           status TEXT DEFAULT 'Incomplete',
                           description TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (email) REFERENCES users(email)
                           PRIMARY KEY (email, task_number)
                            )
                            ''')
            
    # def create_user(self, name: str, email: str, password: str, age: int) -> bool: # create new user
    def create_user(self, email, name, password, age): # create new user
        try:
            with sqlite3.connect(self.db_name) as connect:
                cursor = connect.cursor()
                cursor.execute('''
                    INSERT INTO users (email, name, password, age)
                    VALUES (?, ?, ?, ?)
                    ''', (email, name, password, age)) # column order (<< this part, column order matters refer to line 43)
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
        
    def update_user_fapi(self, new_user_email, old_user_email, name, age): # updates user info
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                UPDATE users
                SET email = ?, name = ?, age = ?
                WHERE email = ?
                ''', (new_user_email, name, age, old_user_email))
            return cursor.rowcount > 0
        
    def create_todo_list(self, email, title, description):
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT MAX (task_number)
                FROM todo 
                WHERE email = ?
                ''', (email,)) # after , is the MAX no.
            result = cursor.fetchone()
            next_number = (result[0] or 0) + 1
            if title == None:
                title = f"TASK_{next_number}"
            if description == None:
                description = f"N/A"
            cursor.execute('''
                INSERT INTO todo (email, task_number, title, description)
                VALUES (?, ?, ?, ?)
                ''', (email, next_number, title, description))
            connect.commit()
            return next_number
        
    def get_users_tasks(self, email, for_checking = 0): # gets all tasks
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            if for_checking > 0:
                cursor.execute('''
                    SELECT t.email, t.task_number, t.title, t.status, t.description, t.created_at
                    FROM todo t
                    WHERE t.email = ? AND t.task_number = ?
                    ORDER BY t.created_at ASC
                    ''', (email, for_checking,))
                return cursor.fetchone()
            
            else:
                cursor.execute('''
                    SELECT t.email, t.task_number, t.title, t.status, t.description, t.created_at
                    FROM todo t
                    WHERE t.email = ?
                    ORDER BY t.created_at ASC
                    ''', (email,))
                return cursor.fetchall()
        
    def update_task_status(self, email, task_number, status): # updates task status
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                UPDATE todo
                SET status = ?
                WHERE email = ? AND task_number = ?
                ''', (status, email, task_number))
            return cursor.rowcount > 0
        
    def update_user_task(self, email, task_number, title, status, description): # updates task status
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                UPDATE todo
                SET title = ?, status = ?, description = ?
                WHERE email = ? AND task_number = ?
                ''', (title, status, description, email, task_number))
            return cursor.rowcount > 0
        
    def delete_task(self, email, task_number): # deletes a task
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                DELETE FROM todo
                WHERE email = ? AND task_number = ?
                ''', (email, task_number))
            return cursor.rowcount > 0
        
    def delete_all_user_task(self, email): # deletes all tasks by user (ADMIN)
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                DELETE FROM todo
                WHERE email = ?
                ''', (email,))
            connect.commit()
            return cursor.rowcount > 0

    def delete_user(self, email): # deletes a user
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM users WHERE email = ?",(email,))
            cursor.execute("DELETE FROM todo WHERE email = ?",(email,))
            connect.commit()
            return cursor.rowcount > 0

    def delete_user_by_oid(self, oid): # deletes a user (ADMIN)
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM users WHERE oid = ?",(oid))
            cursor.execute("DELETE FROM todo WHERE oid = ?",(oid))
            return cursor.rowcount > 0

    def get_user(self, email): # gets all users *Admin only
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT u.oid, u.email, u.name, u.age, u.created_at
                FROM users u
                WHERE email = ?
                ''', (email,))
            return cursor.fetchone()
        
    def get_all_users(self): # gets all users *Admin only
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT * FROM users
                ''')
            return cursor.fetchall()
        
    def get_all_tasks(self): # gets all users *Admin only
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                SELECT * FROM todo
                ''')
            return cursor.fetchall()
        
    def restart(self): # gets all users *Admin only
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
                DELETE FROM users
                ''')
            cursor.execute('''
                DELETE FROM todo
                ''')
            return cursor.rowcount > 0
                
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
    # print("0 VIEW ALL USERS - ADMIN")
    print("1 CREATE USER")
    print("2 CREATE NEW TASK")
    print("22 UPDATE USER")
    print("3 UPDATE TASK")
    print("4 VIEW TASK(S)")
    print("5 DELETE TASK")
    print("6 DELETE USER")
    print("C to Toggle 'Clear the terminal'")
    print("X to EXIT")
    print("="*40) 

# def num_check(*args):
#     inpt = []
#     for i in args:
#         try:
#             # inpt.append(int(i))
#             inpt = int(i)
#         except:
#             print("Invalid entry, must be number")
#             # raise SystemExit
#             return None
#     return args


def num_check(*args):
    inpt = []
    for i in args:
        try:
            inpt.append(int(i))
        except:
            print("Invalid entry, must be number")
            raise SystemExit
            
    return inpt

def clear_terminal(x):
    if x == 0:
        return None
        # return
    if os.name == 'nt':
        os.system('cls')  # Windows command to clear the terminal
        # return None
    else:
        os.system('clear')  # Unix-based command (Linux/macOS) to clear the terminal
        # return None

def verify_user(db, email):
    if email == "" or db.get_user(email) == None:
        input("✗ Email was null or user not found. Press any key to continue ...")
        return "Err"
    return None


def main():
    clear_term = True
    db = db_manager()
    repeat = False

    while True:
        if repeat == 0:
            clear_terminal(clear_term)
            display_menu()
            choice = input("Please enter the the number of displayed options, type 'X' to exit.").strip().lower()
        else:
            choice = input("\nProcess complete. Press Enter to return to menu or enter the numbered keys to carry-on ... ")
            clear_terminal(clear_term)
            display_menu()
            
        if choice == "":
            continue
            
        if choice == 'c' or choice == 'C':
            if clear_term == True:
                clear_term = False
                print(f"Clear terminal was set to 1, now set to {clear_term}")
            else:
                clear_term = True
                print(f"Clear terminal was set to 0, now set to {clear_term}")

        elif choice == '1':
            print("\n --- Create New User --- ")
            email = input("Enter e-mail: ").strip()
            if db.get_user(email) or email == "":
                choice = input ("User exist or was NULL. Press any key to continue ...")
                continue
            name = input("Enter name: ").strip()
            if name == "":
                name = "NULL"
            password = input("Enter password: ").strip()
            if password == "":
                password = "NULL"
            age = input("Enter age (optional): ").strip()
            if age == "":
                age = 0
            user_id = db.create_user(email, name, password, age)
            print(f"✓ User created successfully! E-mail: {user_id}")

        elif choice == '0':
            print("\n --- Get All Users --- ")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if username == "@!" and password == "":
                users = db.get_all_users()
                # print(users)
                if users:
                    for u in users:
                        print(f"Obj_ID: {u[4]}"
                              f"| E-mail: {u[0]}"
                              f"| Name: {u[1]}"
                              f"| Password: {u[2]}"
                              f"| Age: {u[3]}"
                              f"| Time created: {u[5]}")
                else:
                    print("No users found.")
            elif username == "@!" and password == "TASKS":
                users = db.get_all_tasks()
                if users:
                    for u in users:
                        print(f"| E-mail: {u[0]}"
                              f"| task_number: {u[1]}"
                              f"| title: {u[2]}"
                              f"| status: {u[3]}"
                              f"| description: {u[4]}"
                              f"| Time created: {u[5]}")
                else:
                    print("No tasks found.")
            elif username == "@!" and password == "DELETE":
                OBJ_ID = input("OID: ").strip()
                db.delete_user_by_oid(OBJ_ID)
                db.delete_all_user_task(OBJ_ID)
            elif username == "@!" and password == "RESTART":
                comm = input("ZERO OUT DB: Y/N: ").lower()
                if comm == "y":
                    db.restart()
                continue

        elif choice == '2':
            print("\n --- Create New Task --- ")
            email = input("Enter e-mail: ").strip()
            if verify_user(db, email) == "Err":
                continue
            title = input("Enter task: ").strip()
            description = input("Enter remarks for said task: ").strip()
            task = db.create_todo_list(email, title, description)
            if task:
                print(f"✓ Post created successfully! E-mail: {email}")
            else:
                print("✗ Failed to create post")

        elif choice == '22':
            print("\n --- Update User --- ")
            old_user_email = input("Enter current e-mail: ").strip()
            if verify_user(db, email) == "Err":
                continue
            new_user_email = input("Enter new e-mail, leave blank to remain: ").strip()
            name = input("Enter new name, leave blank to remain: ").strip()
            password = input("Enter new password, leave blank to remain: ").strip()
            age = input("Enter new age, leave blank to remain: ").strip()
            if new_user_email == "":
                new_user_email = old_user_email
            if name == "":
                fetch_user[1]
                pass
            if password == "":
                fetch_user[2]
                pass
            if age == "":
                fetch_user[3]
                pass
            db.update_user(new_user_email, old_user_email, name, password, age)
            fetch_user = db.get_user(new_user_email)
            num_of_elements = [
                "email", 
                "name", 
                "password", 
                "age"
                ]
            if fetch_user:
                for v, t in enumerate(fetch_user):
                    print(f"\n{num_of_elements[v]}: {t}")
                    # print(f"Task: {t['title']}")
                    # print(f"Status: {t['status']}")
                    # print(f"Created: {t['created_at']}")
                    print("-" * 30)
            else:
                print("No task(s) found for this user.")
        
        elif choice == '3':
            print("\n --- Update Task --- ")
            email = input("Enter e-mail: ").strip()
            if verify_user(db, email) == "Err":
                continue
            number = input("Please input task number: ").strip()
            status = input("Update status to (In-progress = 0, Done = 1): ").strip()
            number, status = num_check(number, status)
            if status == 1:
                status = "DONE"
            # else:
            #     status = "Incomplete"
            db.update_task_status(email, number, status)
            view_task = db.get_users_tasks(email, number)
            num_of_elements = [
                "email", 
                "task_number", 
                "title", 
                "status", 
                "description", 
                "created_at",
                ]
            if view_task:
                clear_terminal(clear_term)
                print("\n --- Task Updated --- ")
                for v, t in enumerate(view_task):
                    print(f"{num_of_elements[v]}: {t}")
                    # pass
            else:
                print("No task(s) found for this user.")

        elif choice == '4':
            print("\n --- View Task(s) --- ")
            email = input("Enter e-mail: ").strip()
            all_tasks = db.get_users_tasks(email)
            # print(all_tasks)
            if not all_tasks:
                input("Tasks list is empty. Press any key to continue ...")
                continue
            num_of_elements = [
                "\nE-mail",
                "\n#",
                "Title",
                "Status",
                "Description",
                "Created at",
                ]
            view_all = input("Do you wish to view all tasks? (Y/N): ").strip().lower()
            if view_all =="y" and all_tasks:
                email_printed = False
                for t in all_tasks:
                    if email_printed == False:
                        print(f"\nE-mail: {t[0]}")
                        email_printed = True
                    print(f"\n#: {t[1]}")
                    print(f"Title: {t[2]}")
                    print(f"Status: {t[3]}")
                    print(f"Description: {t[4]}")
                    print(f"Created: {t[5]}")
                    print("-" * 30)
            else:
                number = num_check(input("Please input task number: ").strip())
                one_task = db.get_users_tasks(email, number)
                if not one_task:
                    print("Task number does not exis4t.")
                print(f"\nE-mail: {one_task[0]}")
                print(f"\n#: {one_task[1]}")
                print(f"Title: {one_task[2]}")
                print(f"Status: {one_task[3]}")
                print(f"Description: {one_task[4]}")
                print(f"Created: {one_task[5]}")
                print("-" * 30)

        elif choice == '5':
            print("\n --- Delete Task --- ")
            email = input("Enter e-mail: ").strip()
            if verify_user(db, email) == "Err":
                continue
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
            if verify_user(db, email) == "Err":
                continue
            confirm = input(f"Are you sure you want to delete user {email}? (y/N): ").strip().lower()
            if confirm == 'y':
                if db.delete_user(email):
                    print("✓ User deleted successfully!")
                else:
                    print("✗ User not found or deletion failed.")

            else:
                print("Deletion cancelled.")

        elif choice == 'x' or choice == 'X':
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
        repeat = True

def test():
    db = db_manager()

    while True:
        choice = input().strip()
        if choice == '':
            pass

# main()
if __name__ == "__main__":
    main()
    # test()
    pass