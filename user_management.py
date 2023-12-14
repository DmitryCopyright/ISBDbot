import sqlite3
from sqlite3 import Error

def create_connection():
    """ Создать соединение с базой данных SQLite. """
    try:
        conn = sqlite3.connect('library.db')
        return conn
    except Error as e:
        print(e)

def register_user(user):
    """
    Регистрация нового пользователя.
    user - объект пользователя, содержащий имя и контактные данные.
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Предполагаем, что у нас есть поля user.name и user.contact_data
        query = ''' INSERT INTO Readers(name, contact_data, reader_number)
                    VALUES(?,?,?) '''
        cursor.execute(query, (user.name, user.contact_data, user.reader_number))
        conn.commit()
        return cursor.lastrowid  # Возвращает идентификатор нового пользователя

def log_in_user(user):
    """
    Аутентификация пользователя.
    user - объект пользователя, содержащий имя и номер читателя.
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Проверяем, существует ли пользователь с таким именем и номером читателя
        query = ''' SELECT * FROM Readers WHERE name = ? AND reader_number = ? '''
        cursor.execute(query, (user.name, user.reader_number))
        records = cursor.fetchall()
        if records:
            return True  # Пользователь найден
        else:
            return False  # Пользователь не найден

def get_user_profile(user_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, contact_data, reader_number FROM Readers WHERE reader_id = ?", (user_id,))
        return cursor.fetchone()

def user_exists(user_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Readers WHERE reader_id = ?", (user_id,))
        return cursor.fetchone() is not None

def update_user_profile(user_id, name, contact_data):
    if not user_exists(user_id):
        return False  # Пользователь не найден
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Readers SET name = ?, contact_data = ? WHERE reader_id = ?", (name, contact_data, user_id))
        conn.commit()
        return cursor.rowcount > 0