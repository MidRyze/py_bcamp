import sqlite3
import os

def create_table_column(table_name, column_name):
    invalid_entry = (tuple, set, dict)
    if isinstance(table_name, invalid_entry) or isinstance(column_name, invalid_entry):
        return "Wrong type for argument(s)"

class db_manager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS
            ''')