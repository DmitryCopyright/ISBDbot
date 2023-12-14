-- Inserting data into LibraryDepartments
INSERT INTO LibraryDepartments (department_id, name) VALUES
  (1, 'Отдел русской литературы'),
  (2, 'Отдел научной литературы'),
  (3, 'Отдел искусств'),
  (4, 'Отдел зарубежной литературы');

-- Inserting data into Genres
INSERT INTO Genres (genre_id, name) VALUES
  (1, 'Роман'),
  (2, 'Научно-популярное'),
  (3, 'Искусство'),
  (4, 'Фэнтези');

-- Inserting data into Publishers
INSERT INTO Publishers (publisher_id, name) VALUES
  (1, 'Издательство "Русская книга"'),
  (2, 'Издательство "Наука"'),
  (3, 'Издательство "Искусство"'),
  (4, 'Издательство "Фантастика"');

-- Inserting data into Authors
INSERT INTO Authors (author_id, name) VALUES
  (1, 'Александр Пушкин'),
  (2, 'Фёдор Достоевский'),
  (3, 'Лев Толстой'),
  (4, 'Дж. Р. Р. Толкиен'),
  (5, 'Джордж Мартин');

-- Inserting data into LibraryStaff
INSERT INTO LibraryStaff (staff_id, name) VALUES
  (1, 'Екатерина Иванова'),
  (2, 'Алексей Смирнов'),
  (3, 'Ольга Петрова'),
  (4, 'Иван Павлов');

-- Inserting data into Readers
INSERT INTO Readers (reader_id, name, contact_data, reader_number) VALUES
  (1, 'Иван Иванов', 'ivan@example.com', 'R001'),
  (2, 'Мария Смирнова', 'maria@example.com', 'R002'),
  (3, 'Петр Петров', 'petr@example.com', 'R003'),
  (4, 'Анна Иванова', 'anna@example.com', 'R004');

-- Inserting data into Books
INSERT INTO Books (book_id, name, ISBN, author_id, publisher_id, genre_id, department_id, copies) VALUES
  (1, 'Евгений Онегин', '978-5-9573-0422-5', 1, 1, 1, 1, 5),
  (2, 'Преступление и наказание', '978-5-389-05550-2', 2, 2, 1, 1, 8),
  (3, 'Война и мир', '978-5-389-06725-3', 3, 3, 1, 1, 10),
  (4, 'Властелин колец', '978-5-389-19001-3', 4, 4, 4, 1, 6),
  (5, 'Игра престолов', '978-5-389-26001-2', 5, 4, 4, 1, 7),
  (6, 'Анна Каренина', '978-5-389-08711-5', 3, 3, 1, 1, 12),
  (7, 'Процесс', '978-5-17-103855-4', 2, 2, 2, 2, 5);

-- Inserting data into BookLoans
INSERT INTO BookLoans (loan_id, book_id, reader_id, staff_id, issue_date, return_period) VALUES
  (1, 1, 1, 1, '2023-01-01', '2023-01-15'),
  (2, 2, 2, 2, '2023-02-01', '2023-02-15'),
  (3, 3, 3, 3, '2023-03-01', '2023-03-15'),
  (4, 4, 4, 4, '2023-04-01', '2023-04-15'),
  (5, 5, 1, 1, '2023-05-01', '2023-05-15');;

-- Inserting data into Penalties
INSERT INTO Penalties (penalty_id, reader_id, book_id, issue_date, debt_amount) VALUES
  (1, 1, 1, '2023-01-20', 5.00),
  (2, 2, 2, '2023-02-20', 7.50),
  (3, 3, 3, '2023-03-20', 10.00);

-- Inserting data into BookReservations
INSERT INTO BookReservations (reservation_id, name, book_id, reader_id, staff_id, reservation_date) VALUES
  (1, 'Резерв: Евгений Онегин', 1, 1, 1, '2023-01-05'),
  (2, 'Резерв: Преступление и наказание', 2, 2, 2, '2023-02-05'),
  (3, 'Резерв: Война и мир', 3, 3, 3, '2023-03-05'),
  (4, 'Резерв: Властелин колец', 4, 4, 4, '2023-04-05'),
  (5, 'Резерв: Игра престолов', 5, 1, 1, '2023-05-05');

-- Inserting data into Ratings
INSERT INTO Ratings (rate_id, book_id, reader_id, rate_date, rate_amount, rate_text) VALUES
  (1, 1, 1, '2023-01-10', 4, 'Отличная книга!'),
  (2, 2, 2, '2023-02-10', 5, 'Великолепное произведение'),
  (3, 3, 3, '2023-03-10', 4, 'Интересно, но сложно');