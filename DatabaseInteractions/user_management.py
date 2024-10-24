from Configuration.db_operations import *
import psycopg2.extras

from Configuration.localization import MESSAGES


def register_user(name, contact_data, reader_number):
    """
    Регистрирует нового пользователя, если имя не существует в базе данных.
    """
    query = "SELECT * FROM Readers WHERE name = %s"
    if check_if_exists(query, (name,)):
        return MESSAGES["already_registered"]

    user_data = {
        'name': name,
        'contact_data': contact_data,
        'reader_number': reader_number
    }
    return add_record("Readers", user_data, "reader_id")

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
    return get_record_by_id("LibraryStaff", "name", name, "staff_id")

def get_user_profile(user_id):
    """
    Возвращает профиль пользователя по его ID.
    """
    return get_record_by_id("Readers", "reader_id", user_id, "name, contact_data, reader_number")

def user_exists(user_id):
    """
    Проверяет, существует ли пользователь с данным ID.
    """
    return check_if_exists("Readers", "reader_id", user_id)