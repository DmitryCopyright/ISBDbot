import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ Создать соединение с базой данных SQLite, указанной в db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def execute_read_query(conn, query):
    """ Выполнить чтение запроса и вернуть данные """
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(e)

def execute_write_query(conn, query):
    """ Выполнить запись запроса (INSERT, UPDATE, DELETE) """
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except Error as e:
        print(e)
