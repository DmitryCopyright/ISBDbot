from Configuration.db_operations import *
from psycopg2 import sql

from Configuration.localization import MESSAGES


def add_book(name, ISBN, author_id, publisher_id, genre_id, department_id, copies):
    book_data = {
        'name': name,
        'ISBN': ISBN,
        'author_id': author_id,
        'publisher_id': publisher_id,
        'genre_id': genre_id,
        'department_id': department_id,
        'copies': copies,
    }
    return add_record("Books", book_data, "book_id")

def delete_book(book_id):
    return delete_record("Books", "book_id", book_id)

def change_copies(book_id, new_copies):
    update_data = {'copies': new_copies}
    return update_record("Books", update_data, "book_id", book_id)

def add_author(name):
    if check_if_exists("SELECT * FROM Authors WHERE name = %s", (name,)):
        return MESSAGES["author_exists"]

    author_data = {'name': name}
    return add_record("Authors", author_data, "author_id")

def delete_author(author_id):
    return delete_record("Authors", "author_id", author_id)

def add_publisher(name):
    if check_if_exists("SELECT * FROM Publishers WHERE name = %s", (name,)):
        return MESSAGES["publisher_exists"]

    publisher_data = {'name': name}
    return add_record("Publishers", publisher_data, "publisher_id")

def delete_publisher(publisher_id):
    return delete_record("Publishers", "publisher_id", publisher_id)

def add_department(name):
    if check_if_exists("SELECT * FROM LibraryDepartments WHERE name = %s", (name,)):
        return MESSAGES["department_exists"]

    department_data = {'name': name}
    return add_record("LibraryDepartments", department_data, "department_id")

def delete_department(department_id):
    return delete_record("LibraryDepartments", "department_id", department_id)

def add_genre(genre_name):
    if check_if_exists("SELECT genre_id FROM Genres WHERE name = %s", (genre_name,)):
        return MESSAGES["genre_exists"]

    genre_data = {'name': genre_name}
    return add_record("Genres", genre_data, "genre_id")

def delete_genre(genre_id):
    return delete_record("Genres", "genre_id", genre_id)