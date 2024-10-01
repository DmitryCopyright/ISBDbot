from Configuration.db_operations import execute_query
import datetime

def book_available(book_id):
    """
    Проверяет наличие доступных копий книги.
    """
    query = "SELECT copies FROM Books WHERE book_id = %s AND copies > 0"
    return execute_query(query, (book_id,), fetchone=True) is not None

def search_books(query):
    """
    Выполняет поиск книг по названию, с возвратом автора для каждой найденной книги.
    """
    books = []
    book_query = "SELECT book_id, name, author_id FROM Books WHERE name LIKE %s"
    rows = execute_query(book_query, ('%' + query + '%',), fetchall=True)

    for row in rows:
        author_query = "SELECT name FROM Authors WHERE author_id = %s"
        author = execute_query(author_query, (row[2],), fetchone=True)[0]
        books.append({'book_id': row[0], 'name': row[1], 'author': author})

    return books

def get_book_details(book_id):
    """
    Получает подробную информацию о книге, включая автора и жанр.
    """
    book_query = "SELECT name, ISBN, author_id, genre_id, copies FROM Books WHERE book_id = %s"
    row = execute_query(book_query, (book_id,), fetchone=True)

    if row:
        author_query = "SELECT name FROM Authors WHERE author_id = %s"
        author = execute_query(author_query, (row[2],), fetchone=True)[0]

        genre_query = "SELECT name FROM Genres WHERE genre_id = %s"
        genre = execute_query(genre_query, (row[3],), fetchone=True)[0]

        return {'name': row[0], 'ISBN': row[1], 'author': author, 'genre': genre, 'copies': row[4]}

    return None

def get_available_books():
    """
    Получает список доступных книг с их авторами.
    """
    query = """
        SELECT Books.book_id, Books.name, Authors.name 
        FROM Books
        JOIN Authors ON Books.author_id = Authors.author_id
        WHERE copies > 0
    """
    rows = execute_query(query, fetchall=True)
    available_books = [{'book_id': row[0], 'name': row[1], 'author': row[2]} for row in rows]

    return available_books

def reserve_book(book_id, reader_id):
    """
    Резервирует книгу для пользователя, создает бронь и запись о выдаче книги.
    """
    # Проверяем, есть ли у пользователя уже активные бронирования
    query = """
        SELECT COUNT(*) FROM BookReservations
        WHERE reader_id = %s AND reservation_date IS NOT NULL
    """
    if execute_query(query, (reader_id,), fetchone=True)[0] >= 1:
        return "Одновременно допускается не больше одного бронирования!"

    # Проверяем наличие книги и пользователя
    query = """
        SELECT b.name, COUNT(br.book_id)
        FROM Books b 
        LEFT JOIN BookReservations br ON br.book_id = b.book_id AND br.reader_id = %s AND br.reservation_date IS NOT NULL
        WHERE b.book_id = %s
        GROUP BY b.name
    """
    result = execute_query(query, (reader_id, book_id), fetchone=True)

    if not result or result[1] > 0:
        return None  # Книга не найдена или уже забронирована пользователем

    book_title = result[0]

    # Создаем бронь в BookReservations
    query = """
        INSERT INTO BookReservations (name, book_id, reader_id, staff_id, reservation_date) 
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
    """
    execute_query(query, (book_title, book_id, reader_id, 1))

    # Создаем запись в BookLoans
    return_date = datetime.date.today() + datetime.timedelta(days=14)
    query = """
        INSERT INTO BookLoans (book_id, reader_id, staff_id, issue_date, return_period) 
        VALUES (%s, %s, %s, CURRENT_DATE, %s)
    """
    execute_query(query, (book_id, reader_id, 1, return_date))

    # Уменьшаем количество доступных копий
    query = "UPDATE Books SET copies = copies - 1 WHERE book_id = %s"
    execute_query(query, (book_id,))

    return "Книга успешно забронирована", return_date

def get_user_reservations(reader_id):
    """
    Возвращает список текущих бронирований пользователя.
    """
    query = """
        SELECT br.reservation_id, b.name, br.reservation_date 
        FROM BookReservations br
        JOIN Books b ON br.book_id = b.book_id
        WHERE br.reader_id = %s
    """
    rows = execute_query(query, (reader_id,), fetchall=True)
    reservations = [{'reservation_id': row[0], 'book_name': row[1], 'reservation_date': row[2]} for row in rows]

    return reservations
