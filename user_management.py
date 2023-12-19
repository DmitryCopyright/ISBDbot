from psycopg2 import extras
from db import *

def register_user(name, contact_data, reader_number):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Проверка на существование пользователя с таким именем
            cursor.execute("SELECT * FROM Readers WHERE name = %s", (name,))
            if cursor.fetchone():
                return "Такое имя пользователя уже зарегистрировано!"

            # Регистрация пользователя
            query = '''INSERT INTO Readers(name, contact_data, reader_number)
                       VALUES(%s, %s, %s) RETURNING reader_id'''
            cursor.execute(query, (name, contact_data, reader_number))
            conn.commit()
            return cursor.fetchone()[0]  # Возвращает идентификатор нового пользователя


def log_in_user(name, reader_number):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            query = '''SELECT reader_id FROM Readers WHERE name = %s AND reader_number = %s'''
            cursor.execute(query, (name, reader_number))
            result = cursor.fetchone()
            return result[0] if result else None

def get_user_profile(user_id):
    conn = create_connection()
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT name, contact_data, reader_number FROM Readers WHERE reader_id = %s", (user_id,))
            return cursor.fetchone()

def user_exists(user_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM Readers WHERE reader_id = %s", (user_id,))
            return cursor.fetchone() is not None
