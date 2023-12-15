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
        # Использование %s вместо ?
        cursor.execute("SELECT name, ISBN, author_id, copies FROM Books WHERE book_id = %s", (book_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("SELECT name FROM Authors WHERE author_id = %s", (row[2],))
            author = cursor.fetchone()[0]
            return {'name': row[0], 'ISBN': row[1], 'author': author, 'copies': row[3]}
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

def reserve_book(book_id, user_number):
    if not book_available(book_id):
        return None  # Книга не доступна для бронирования

    conn = create_connection()
    with conn:
        cursor = conn.cursor()


        # Получаем reader_id и название книги
        cursor.execute("""
            SELECT r.reader_id, b.name 
            FROM Readers r 
            JOIN Books b ON b.book_id = %s 
            WHERE r.reader_number = %s
        """, (book_id, user_number))
        result = cursor.fetchone()
        if cursor.rowcount == 0:
            return None  # Читатель или книга не найдены

        reader_id, book_title = result

        cursor.execute("SELECT COUNT(*) FROM BookReservations WHERE book_id = %s AND reader_id = %s AND reservation_date IS NOT NULL", (book_id, reader_id))
        if cursor.fetchone()[0] > 0:
            return "Вы уже забронировали эту книгу."  # Пользователь уже арендовал эту книгу

        # Создаем бронь в BookReservations
        cursor.execute("""
            INSERT INTO BookReservations (name, book_id, reader_id, staff_id, reservation_date) 
            VALUES (%s, %s, %s, %s, CURRENT_DATE)
        """, (book_title, book_id, reader_id, 1))  # предполагая, что staff_id = 0
        reservation_id = cursor.lastrowid

        # Создаем запись в BookLoans
        return_date = datetime.date.today() + datetime.timedelta(days=14)
        cursor.execute("""
            INSERT INTO BookLoans (book_id, reader_id, staff_id, issue_date, return_period) 
            VALUES (%s, %s, %s, CURRENT_DATE, %s)
        """, (book_id, reader_id, 1, return_date))  # предполагая, что staff_id = 0
        loan_id = cursor.lastrowid

        # Уменьшаем количество доступных копий
        cursor.execute("UPDATE Books SET copies = copies - 1 WHERE book_id = %s", (book_id,))
        conn.commit()

        return reservation_id, loan_id, return_date

def get_user_reservations(reader_number):
    conn = create_connection()
    reservations = []
    with conn:
        cursor = conn.cursor()

        # Получение reader_id по reader_number
        cursor.execute("SELECT reader_id FROM Readers WHERE reader_number = %s", (reader_number,))
        result = cursor.fetchone()
        if not result:
            return []  # Читатель с таким номером не найден
        reader_id = result[0]

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
