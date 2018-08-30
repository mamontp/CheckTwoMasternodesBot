# -*- coding: utf-8 -*-

import sqlite3

class SQLighter:

    def __init__(self, database):
        try:
            self.connection = sqlite3.connect(database)
            self.cursor = self.connection.cursor()
        except Error as e:
            print(e)

    # Create a table if it does not exist.
    def create_tabl(self):
        self.cursor.execute('''CREATE TABLE if not exists users_address (chat_id varchar, coin varchar, address varchar)''')

    # Get all the rows from the table.
    def select_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users_address').fetchall()

    # Adding to the database coin and address for user chat_id
    def add_address(self, chat_id, coin, address):
        row = (chat_id, coin, address)
        result = self.cursor.execute('SELECT * FROM users_address WHERE chat_id=? AND coin=? AND address=?', (row)).fetchall()
        if len(result) == 0:
            #print ("No row")
            with self.connection:
                self.cursor.execute("INSERT INTO users_address VALUES (?, ?, ?)", row)
                self.connection.commit()
        else:
            print ("The coins and address already exist.")
            print (result)

    # get all the rows for a specific number chat_id
    def select_chat_id(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users_address WHERE chat_id = ?', (chat_id,)).fetchall()

    # Count the total number of rows in the table
    def count_rows(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM users_address').fetchall()
            return len(result)

    # Get all the unique chat_id
    def get_all_chat_id(self):
        with self.connection:
            result = self.cursor.execute('SELECT DISTINCT chat_id FROM users_address').fetchall()
            return result

    # Delete from the database coin and address for user chat_id
    def delete_row(self, chat_id, coin, address):
        row = (chat_id, coin, address)
        result = self.cursor.execute('SELECT * FROM users_address WHERE chat_id=? AND coin=? AND address=?', (row)).fetchall()
        if len(result) == 0:
            return ("No address found for deletion.")
        else:
            with self.connection:
                self.cursor.execute("DELETE FROM users_address WHERE chat_id=? AND coin=? AND address=?", (row))
                self.connection.commit()
            return ("The address has been deleted.")

    # Closing the current connection to the database
    def close(self):
        self.connection.close()
