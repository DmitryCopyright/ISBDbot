
import logging
from functools import wraps

from Configuration.db import create_connection


def execute_query(query, params=None, fetchone=False, fetchall=False):
    conn = create_connection()
    result = None
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            conn.commit()
    return result


def check_if_exists(query, params):
    result = execute_query(query, params, fetchone=True)
    return result is not None

def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return None
    return wrapper

def add_record(table, data, returning_field):
    """
    Универсальная функция для добавления записи в любую таблицу.

    :param table: название таблицы
    :param data: словарь с данными для вставки
    :param returning_field: поле, которое будет возвращено после вставки (обычно первичный ключ)
    :return: значение поля returning_field для добавленной записи
    """
    columns = ', '.join(data.keys())
    values = ', '.join([f"%({key})s" for key in data.keys()])

    query = f"INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING {returning_field}"
    return execute_query(query, data, fetchone=True)[0]
def delete_record(table, key_column, key_value):
    """
    Универсальная функция для удаления записи из любой таблицы по ключевому полю.

    :param table: название таблицы
    :param key_column: поле, по которому будет удаляться запись (обычно первичный ключ)
    :param key_value: значение ключевого поля
    :return: True, если удаление прошло успешно
    """
    query = f"DELETE FROM {table} WHERE {key_column} = %s"
    return execute_query(query, (key_value,), fetchone=False)

def update_record(table, update_data, key_column, key_value):
    """
    Универсальная функция для обновления записи в любой таблице.

    :param table: название таблицы
    :param update_data: словарь с обновляемыми данными
    :param key_column: поле, по которому будет идентифицирована запись для обновления
    :param key_value: значение ключевого поля
    :return: True, если обновление прошло успешно
    """
    set_clause = ', '.join([f"{key} = %({key})s" for key in update_data.keys()])

    query = f"UPDATE {table} SET {set_clause} WHERE {key_column} = %s"
    update_data['key_value'] = key_value
    return execute_query(query, update_data, fetchone=False)

def get_record_by_id(table, key_column, key_value, fields="*"):
    """
    Получает запись из таблицы по идентификатору.

    :param table: название таблицы
    :param key_column: поле идентификатора (например, "book_id")
    :param key_value: значение идентификатора
    :param fields: поля, которые нужно выбрать (по умолчанию *)
    :return: возвращает одну запись, если найдена
    """
    query = f"SELECT {fields} FROM {table} WHERE {key_column} = %s"
    return execute_query(query, (key_value,), fetchone=True)