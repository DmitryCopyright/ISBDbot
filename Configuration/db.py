import psycopg2
from psycopg2 import extras

def create_connection():
    """ Создать соединение с базой данных PostgreSQL. """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="studs",
            user="s335065",
            password="RnIXdSSUHSXRZDkr",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(e)
    return conn

def execute_read_query(conn, query):
    """ Выполнить чтение запроса и вернуть данные """
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except psycopg2.Error as e:
            print(e)

def execute_write_query(conn, query):
    """ Выполнить запись запроса (INSERT, UPDATE, DELETE) """
    with conn.cursor() as cursor:
        try:
            cursor.execute(query)
            conn.commit()
        except psycopg2.Error as e:
            print(e)
