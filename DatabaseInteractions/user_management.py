from Configuration.db_operations import *
import psycopg2.extras

def register_user(name, contact_data, reader_number):
    """
    Регистрирует нового пользователя, если имя не существует в базе данных.
    """
    # Проверка на существование пользователя с таким именем
    if check_if_exists("SELECT * FROM Readers WHERE name = %s", (name,)):
        return "Такое имя пользователя уже зарегистрировано!"

    # Регистрация пользователя
    query = '''INSERT INTO Readers(name, contact_data, reader_number)
               VALUES(%s, %s, %s) RETURNING reader_id'''
    return execute_query(query, (name, contact_data, reader_number), fetchone=True)[0]

def log_in_user(name, reader_number):
    """
    Проверяет существование пользователя в базе данных по имени и номеру читателя.
    """
    query = '''SELECT reader_id FROM Readers WHERE name = %s AND reader_number = %s'''
    result = execute_query(query, (name, reader_number), fetchone=True)
    return result[0] if result else None

def log_in_staff(name):
    """
    Проверяет существование сотрудника в базе данных по имени.
    """
    query = '''SELECT staff_id FROM LibraryStaff WHERE name = %s'''
    result = execute_query(query, (name,), fetchone=True)
    return result[0] if result else None

def get_user_profile(user_id):
    """
    Возвращает профиль пользователя по его ID.
    """
    query = '''SELECT name, contact_data, reader_number FROM Readers WHERE reader_id = %s'''
    return execute_query(query, (user_id,), fetchone=True)

def user_exists(user_id):
    """
    Проверяет, существует ли пользователь с данным ID.
    """
    return check_if_exists("SELECT 1 FROM Readers WHERE reader_id = %s", (user_id,))
