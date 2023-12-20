from db import *

def add_book(name, ISBN, author_id, publisher_id, genre_id, department_id, copies):
    conn = create_connection()

    if conn is not None:
        try:
            with conn:
                with conn.cursor() as cursor:
                    # Insert the book into the Books table without specifying book_id
                    book_data = {
                        'name': name,
                        'ISBN': ISBN,
                        'author_id': author_id,
                        'publisher_id': publisher_id,
                        'genre_id': genre_id,
                        'department_id': department_id,
                        'copies': copies,
                    }

                    cursor.execute("""
                        INSERT INTO Books (name, ISBN, author_id, publisher_id, genre_id, department_id, copies)
                        VALUES (%(name)s, %(ISBN)s, %(author_id)s, %(publisher_id)s, %(genre_id)s, %(department_id)s, %(copies)s)
                        RETURNING book_id;
                    """, book_data)

                    book_id = cursor.fetchone()[0]

                    print(f"Book with ID {book_id} added successfully.")
                    return book_id  # Returns the ID of the newly added book

        except psycopg2.Error as e:
            print(f"Error: Unable to add book to the database\n{e}")
        finally:
            conn.close()

def delete_book(book_id):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            # Delete the book with the given ID
            cursor.execute("DELETE FROM Books WHERE book_id = %s", (book_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting book with ID {book_id}: {e}")
        return False

def change_copies(book_id, new_copies):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            # Update the number of copies for the book with the given ID
            cursor.execute("UPDATE Books SET copies = %s WHERE book_id = %s", (new_copies, book_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error changing copies for book with ID {book_id}: {e}")
        return False

def add_author(name):
    conn = create_connection()

    if conn is not None:
        try:
            with conn:
                with conn.cursor() as cursor:
                    # Check if the author with the given name already exists
                    cursor.execute("SELECT * FROM Authors WHERE name = %s", (name,))
                    existing_author = cursor.fetchone()

                    if existing_author:
                        return "Автор с таким именем уже существует!"

                    # Add the author to the Authors table
                    query = '''INSERT INTO Authors(name) VALUES(%s) RETURNING author_id'''
                    cursor.execute(query, (name,))
                    conn.commit()

                    return cursor.fetchone()[0]  # Returns the ID of the newly added author

        except psycopg2.Error as e:
            print(f"Error: Unable to add author to the database\n{e}")
        finally:
            conn.close()

def delete_author(author_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Check if the author exists
            cursor.execute("SELECT * FROM Authors WHERE author_id = %s", (author_id,))
            existing_author = cursor.fetchone()

            if not existing_author:
                return False

            # Delete the author
            cursor.execute("DELETE FROM Authors WHERE author_id = %s", (author_id,))
            conn.commit()
            return True

def add_publisher(name):
    conn = create_connection()

    if conn is not None:
        try:
            with conn:
                with conn.cursor() as cursor:
                    # Check if the publisher with the given name already exists
                    cursor.execute("SELECT * FROM Publishers WHERE name = %s", (name,))
                    existing_publisher = cursor.fetchone()

                    if existing_publisher:
                        return "Издатель с таким именем уже существует!"

                    # Add the publisher to the Publishers table
                    query = '''INSERT INTO Publishers(name) VALUES(%s) RETURNING publisher_id'''
                    cursor.execute(query, (name,))
                    conn.commit()

                    return cursor.fetchone()[0]  # Returns the ID of the newly added publisher

        except psycopg2.Error as e:
            print(f"Error: Unable to add publisher to the database\n{e}")
        finally:
            conn.close()

def delete_publisher(publisher_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Check if the publisher exists
            cursor.execute("SELECT * FROM Publishers WHERE publisher_id = %s", (publisher_id,))
            existing_publisher = cursor.fetchone()

            if not existing_publisher:
                return False

            # Delete the publisher
            cursor.execute("DELETE FROM Publishers WHERE publisher_id = %s", (publisher_id,))
            conn.commit()
            return True

def add_department(name):
    conn = create_connection()

    if conn is not None:
        try:
            with conn:
                with conn.cursor() as cursor:
                    # Check if the department with the given name already exists
                    cursor.execute("SELECT * FROM LibraryDepartments WHERE name = %s", (name,))
                    existing_department = cursor.fetchone()

                    if existing_department:
                        return "Отдел с таким именем уже существует!"

                    # Add the department to the LibraryDepartments table
                    query = '''INSERT INTO LibraryDepartments(name) VALUES(%s) RETURNING department_id'''
                    cursor.execute(query, (name,))
                    conn.commit()

                    return cursor.fetchone()[0]  # Returns the ID of the newly added department

        except psycopg2.Error as e:
            print(f"Error: Unable to add department to the database\n{e}")
        finally:
            conn.close()

def delete_department(department_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Check if the department exists
            cursor.execute("SELECT * FROM LibraryDepartments WHERE department_id = %s", (department_id,))
            existing_department = cursor.fetchone()

            if not existing_department:
                return False

            # Delete the department
            cursor.execute("DELETE FROM LibraryDepartments WHERE department_id = %s", (department_id,))
            conn.commit()
            return True

def add_genre(genre_name):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Check if the genre already exists
            cursor.execute("SELECT genre_id FROM Genres WHERE name = %s", (genre_name,))
            existing_genre = cursor.fetchone()

            if existing_genre:
                return existing_genre[0]

            # Add the new genre
            cursor.execute("INSERT INTO Genres (name) VALUES (%s) RETURNING genre_id", (genre_name,))
            conn.commit()
            return cursor.fetchone()[0]

def delete_genre(genre_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            # Check if the genre exists
            cursor.execute("SELECT * FROM Genres WHERE genre_id = %s", (genre_id,))
            existing_genre = cursor.fetchone()

            if not existing_genre:
                return False

            # Delete the genre
            cursor.execute("DELETE FROM Genres WHERE genre_id = %s", (genre_id,))
            conn.commit()
            return True