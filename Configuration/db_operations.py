
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