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
    def create_tabl(self, table_name):
        create_table = {'user_nodes': 'CREATE TABLE if not exists {table_name} (chat_id varchar, coin varchar, address varchar, node varchar, last varchar)',
                        'users_address': 'CREATE TABLE if not exists {table_name} (chat_id varchar, coin varchar, address varchar)'}
        try:
            inquiry = create_table[table_name]
            self.cursor.execute(inquiry.format(table_name=table_name))
            return 'Ok'
        except KeyError as e:
            return 'Undefined table name: {}'.format(e.args[0])

    # Adding last time form the node or update last time
    def add_paidAt(self, table_name, chat_id, coin, address, masternode, time_now):
        row = (chat_id, coin, address, masternode)
        inquiry = 'SELECT * FROM {table_name} WHERE chat_id=? AND coin=? AND address=? AND node=?'
        result = self.cursor.execute(inquiry.format(table_name=table_name), (row)).fetchall()
        if len(result) == 0:
            #print ("No row")
            with self.connection:
                row = (chat_id, coin, address, masternode, time_now)
                inquiry = 'INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)'
                self.cursor.execute(inquiry.format(table_name=table_name), row)
                self.connection.commit()
        else:
            with self.connection:
                row = (time_now, chat_id, coin, address, masternode)
                inquiry = 'UPDATE {table_name} SET last=? WHERE chat_id=? AND coin=? AND address=? AND node=?'
                self.cursor.execute(inquiry.format(table_name=table_name), row)
                self.connection.commit()

    # Get all the rows from the table.
    def select_all(self, table_name):
        with self.connection:
            inquiry = 'SELECT * FROM {table_name}'
            return self.cursor.execute(inquiry.format(table_name=table_name)).fetchall()

    # Get last time from DB
    def get_last(self, table_name, chat_id, coin, address, masternode):
        row = (chat_id, coin, address, masternode)
        inquiry = 'SELECT last FROM {table_name} WHERE chat_id=? AND coin=? AND address=? AND node=?'
        result = self.cursor.execute(inquiry.format(table_name=table_name), (row)).fetchall()
        return result

    def update_last(self, table_name, last):
        inquiry = 'UPDATE {table_name} SET last=?'
        self.cursor.execute(inquiry.format(table_name=table_name), (last,))
        self.connection.commit()

    # Adding to the database coin and address for user chat_id
    def add_address(self, table_name, chat_id, coin, address):
        row = (chat_id, coin, address)
        inquiry = 'SELECT * FROM {table_name} WHERE chat_id=? AND coin=? AND address=?'
        result = self.cursor.execute(inquiry.format(table_name=table_name), (row)).fetchall()
        if len(result) == 0:
            #print ("No row")
            with self.connection:
                inquiry = 'INSERT INTO {table_name} VALUES (?, ?, ?)'
                self.cursor.execute(inquiry.format(table_name=table_name), row)
                self.connection.commit()
        else:
            print ("The coins and address already exist.")
            print (result)

    # get all the rows for a specific number chat_id
    def select_chat_id(self, table_name, chat_id):
        with self.connection:
            inquiry = 'SELECT * FROM {table_name} WHERE chat_id = ?'
            return self.cursor.execute(inquiry.format(table_name=table_name), (chat_id,)).fetchall()

    # get all the rows for a specific coin
    def select_coin(self, table_name, coin):
        with self.connection:
            inquiry = 'SELECT * FROM {table_name} WHERE coin = ?'
            return self.cursor.execute(inquiry.format(table_name=table_name), (coin,)).fetchall()

    # get all the rows for a specific address
    def select_address(self, table_name, address):
        with self.connection:
            inquiry = 'SELECT * FROM {table_name} WHERE address = ?'
            return self.cursor.execute(inquiry.format(table_name=table_name), (address,)).fetchall()

    # Count the total number of rows in the table
    def count_rows(self, table_name):
        with self.connection:
            inquiry = 'SELECT * FROM {table_name}'
            result = self.cursor.execute(inquiry.format(table_name=table_name)).fetchall()
            return len(result)

    # Get all the unique chat_id
    def get_all_chat_id(self, table_name):
        with self.connection:
            inquiry = 'SELECT DISTINCT chat_id FROM {table_name}'
            result = self.cursor.execute(inquiry.format(table_name=table_name)).fetchall()
            return result

    # Delete from the database coin and address for user chat_id
    def delete_row(self, table_name, chat_id, coin, address):
        row = (chat_id, coin, address)
        inquiry = 'SELECT * FROM {table_name} WHERE chat_id=? AND coin=? AND address=?'
        result = self.cursor.execute(inquiry.format(table_name=table_name), (row)).fetchall()
        if len(result) == 0:
            return ("No address found for deletion.")
        else:
            with self.connection:
                inquiry = 'DELETE FROM {table_name} WHERE chat_id=? AND coin=? AND address=?'
                self.cursor.execute(inquiry.format(table_name=table_name), (row))
                self.connection.commit()
            return ("The address has been deleted.")

    # Closing the current connection to the database
    def close(self):
        self.connection.close()
