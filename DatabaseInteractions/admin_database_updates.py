from Configuration.db_operations import *
from psycopg2 import sql

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
    query = '''
        INSERT INTO Books (name, ISBN, author_id, publisher_id, genre_id, department_id, copies)
        VALUES (%(name)s, %(ISBN)s, %(author_id)s, %(publisher_id)s, %(genre_id)s, %(department_id)s, %(copies)s)
        RETURNING book_id;
    '''
    return execute_query(query, book_data, fetchone=True)[0]

def delete_book(book_id):
    query = "DELETE FROM Books WHERE book_id = %s"
    return execute_query(query, (book_id,), fetchone=False)

def change_copies(book_id, new_copies):
    query = "UPDATE Books SET copies = %s WHERE book_id = %s"
    return execute_query(query, (new_copies, book_id), fetchone=False)

def add_author(name):
    if check_if_exists("SELECT * FROM Authors WHERE name = %s", (name,)):
        return "Автор с таким именем уже существует!"
    query = '''INSERT INTO Authors(name) VALUES(%s) RETURNING author_id'''
    return execute_query(query, (name,), fetchone=True)[0]

def delete_author(author_id):
    query = "DELETE FROM Authors WHERE author_id = %s"
    return execute_query(query, (author_id,), fetchone=False)

def add_publisher(name):
    if check_if_exists("SELECT * FROM Publishers WHERE name = %s", (name,)):
        return "Издатель с таким именем уже существует!"
    query = '''INSERT INTO Publishers(name) VALUES(%s) RETURNING publisher_id'''
    return execute_query(query, (name,), fetchone=True)[0]

def delete_publisher(publisher_id):
    query = "DELETE FROM Publishers WHERE publisher_id = %s"
    return execute_query(query, (publisher_id,), fetchone=False)

def add_department(name):
    if check_if_exists("SELECT * FROM LibraryDepartments WHERE name = %s", (name,)):
        return "Отдел с таким именем уже существует!"
    query = '''INSERT INTO LibraryDepartments(name) VALUES(%s) RETURNING department_id'''
    return execute_query(query, (name,), fetchone=True)[0]

def delete_department(department_id):
    query = "DELETE FROM LibraryDepartments WHERE department_id = %s"
    return execute_query(query, (department_id,), fetchone=False)

def add_genre(genre_name):
    query = '''SELECT genre_id FROM Genres WHERE name = %s'''
    existing_genre = execute_query(query, (genre_name,), fetchone=True)

    if existing_genre:
        return existing_genre[0]

    query = "INSERT INTO Genres (name) VALUES (%s) RETURNING genre_id"
    return execute_query(query, (genre_name,), fetchone=True)[0]

def delete_genre(genre_id):
    query = "DELETE FROM Genres WHERE genre_id = %s"
    return execute_query(query, (genre_id,), fetchone=False)
