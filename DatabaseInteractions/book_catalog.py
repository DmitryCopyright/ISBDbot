import datetime
from db import *

def book_available(book_id):
    conn = create_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT copies FROM Books WHERE book_id = %s AND copies > 0", (book_id,))
            return cursor.fetchone() is not None

def search_books(query):
    conn = create_connection()
    books = []
    with conn:
        cursor = conn.cursor()

        cursor.execute("SELECT book_id, name, author_id FROM Books WHERE name LIKE %s", ('%'+query+'%',))
        rows = cursor.fetchall()
        for row in rows:
            cursor.execute("SELECT name FROM Authors WHERE author_id = %s", (row[2],))
            author = cursor.fetchone()[0]
            books.append({'book_id': row[0], 'name': row[1], 'author': author})
    return books

def get_book_details(book_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ISBN, author_id, genre_id, copies FROM Books WHERE book_id = %s", (book_id,))
        row = cursor.fetchone()
        if row:
            # Fetch author name
            cursor.execute("SELECT name FROM Authors WHERE author_id = %s", (row[2],))
            author = cursor.fetchone()[0]

            # Fetch genre name
            cursor.execute("SELECT name FROM Genres WHERE genre_id = %s", (row[3],))
            genre = cursor.fetchone()[0]

            return {'name': row[0], 'ISBN': row[1], 'author': author, 'genre': genre, 'copies': row[4]}
        else:
            return None

def get_available_books():
    conn = create_connection()
    available_books = []
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Books.book_id, Books.name, Authors.name 
            FROM Books
            JOIN Authors ON Books.author_id = Authors.author_id
            WHERE copies > 0
        """)
        rows = cursor.fetchall()
        for row in rows:
            available_books.append({'book_id': row[0], 'name': row[1], 'author': row[2]})
    return available_books

def reserve_book(book_id, reader_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        # Проверяем, есть ли у пользователя уже активные бронирования
        cursor.execute("""
            SELECT COUNT(*) FROM BookReservations
            WHERE reader_id = %s AND reservation_date IS NOT NULL
        """, (reader_id,))
        if cursor.fetchone()[0] >= 1:
            return "Одновременно допускается не больше одного бронирования!"

        # Проверяем наличие книги и пользователя, а также предыдущие бронирования
        cursor.execute("""
            SELECT b.name, COUNT(br.book_id)
            FROM Books b 
            LEFT JOIN BookReservations br ON br.book_id = b.book_id AND br.reader_id = %s AND br.reservation_date IS NOT NULL
            WHERE b.book_id = %s
            GROUP BY b.name
        """, (reader_id, book_id))
        result = cursor.fetchone()

        if cursor.rowcount == 0 or result[1] > 0:
            return None  # Книга не найдена или уже забронирована пользователем

        book_title = result[0]

        # Создаем бронь в BookReservations
        cursor.execute("""
            INSERT INTO BookReservations (name, book_id, reader_id, staff_id, reservation_date) 
            VALUES (%s, %s, %s, %s, CURRENT_DATE)
        """, (book_title, book_id, reader_id, 0))  # Используйте фактический staff_id
        reservation_id = cursor.lastrowid

        # Создаем запись в BookLoans
        return_date = datetime.date.today() + datetime.timedelta(days=14)
        cursor.execute("""
            INSERT INTO BookLoans (book_id, reader_id, staff_id, issue_date, return_period) 
            VALUES (%s, %s, %s, CURRENT_DATE, %s)
        """, (book_id, reader_id, 0, return_date))  # Используйте фактический staff_id
        loan_id = cursor.lastrowid

        # Уменьшаем количество доступных копий
        cursor.execute("UPDATE Books SET copies = copies - 1 WHERE book_id = %s", (book_id,))
        conn.commit()

        return reservation_id, loan_id, return_date


def get_user_reservations(reader_id):
    conn = create_connection()
    reservations = []
    with conn:
        cursor = conn.cursor()

        # Получение резерваций по reader_id
        cursor.execute("""
            SELECT br.reservation_id, b.name, br.reservation_date 
            FROM BookReservations br
            JOIN Books b ON br.book_id = b.book_id
            WHERE br.reader_id = %s
        """, (reader_id,))
        rows = cursor.fetchall()
        for row in rows:
            reservations.append({'reservation_id': row[0], 'book_name': row[1], 'reservation_date': row[2]})

    return reservations
