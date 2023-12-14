import sqlite3

from user_management import user_exists


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('library.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def book_available(book_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT copies FROM Books WHERE book_id = ? AND copies > 0", (book_id,))
        return cursor.fetchone() is not None

def search_books(query):
    conn = create_connection()
    books = []
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, name, author_id FROM Books WHERE name LIKE ?", ('%'+query+'%',))
        rows = cursor.fetchall()
        for row in rows:
            # Добавляем информацию об авторе из таблицы Authors
            cursor.execute("SELECT name FROM Authors WHERE author_id = ?", (row[2],))
            author = cursor.fetchone()[0]
            books.append({'book_id': row[0], 'name': row[1], 'author': author})
    return books

def get_book_details(book_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ISBN, author_id, copies FROM Books WHERE book_id = ?", (book_id,))
        row = cursor.fetchone()
        if row:
            # Добавляем информацию об авторе из таблицы Authors
            cursor.execute("SELECT name FROM Authors WHERE author_id = ?", (row[2],))
            author = cursor.fetchone()[0]
            return {'name': row[0], 'ISBN': row[1], 'author': author, 'copies': row[3]}
        else:
            return None

def get_available_books():
    conn = create_connection()
    available_books = []
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, name FROM Books WHERE copies > 0")
        rows = cursor.fetchall()
        for row in rows:
            available_books.append({'book_id': row[0], 'name': row[1]})
    return available_books

def reserve_book(book_id, user_id):
    if not book_available(book_id):
        return None  # Книга не доступна для бронирования
    if not user_exists(user_id):
        return None  # Пользователь не найден
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Создаем бронь
        cursor.execute("INSERT INTO BookReservations (book_id, reader_id, reservation_date) VALUES (?, ?, CURRENT_DATE)", (book_id, user_id))
        # Уменьшаем количество доступных копий
        cursor.execute("UPDATE Books SET copies = copies - 1 WHERE book_id = ?", (book_id,))
        conn.commit()
        return cursor.lastrowid

def get_user_reservations(user_id):
    conn = create_connection()
    reservations = []
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT reservation_id, book_id, reservation_date FROM BookReservations WHERE reader_id = ?", (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            # Добавляем информацию о книге
            cursor.execute("SELECT name FROM Books WHERE book_id = ?", (row[1],))
            book_name = cursor.fetchone()[0]
            reservations.append({'reservation_id': row[0], 'book_name': book_name, 'reservation_date': row[2]})
    return reservations