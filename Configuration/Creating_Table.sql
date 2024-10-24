create table if not exists LibraryDepartments
(
    department_id   serial primary key,
    name            varchar(50) not null
);

create table if not exists Genres
(
    genre_id        serial primary key,
    name            varchar(50) not null
);

create table if not exists Publishers
(
    publisher_id    serial primary key,
    name            varchar(50) not null
);

create table if not exists Authors
(
    author_id   serial primary key,
    name        varchar(50) not null
);

create table if not exists LibraryStaff
(
    staff_id        serial primary key,
    name            varchar(50) not null
);

create table if not exists Readers
(
    reader_id      serial primary key,
    name           varchar(50) not null,
    contact_data   varchar(50) not null,
    reader_number  varchar(50) not null
);

create table if not exists Books
(
    book_id     serial primary key,
    name        varchar(50) not null,
    ISBN        varchar(50) not null,
    author_id         int not null
        references Authors (author_id),
    publisher_id        int not null
        references Publishers (publisher_id),
    genre_id            int not null
        references Genres (genre_id),
    department_id       int not null
        references LibraryDepartments (department_id),
    copies      integer
);

create table if not exists BookLoans
(
    loan_id         serial primary key,
    book_id         int not null
        references Books (book_id),
    reader_id       int not null
        references Readers (reader_id),
    staff_id           int not null
        references LibraryStaff (staff_id),
    issue_date      DATE,
    return_period   DATE
);

create table if not exists Penalties
(
    penalty_id      serial primary key,
    reader_id       int not null
        references Readers (reader_id),
    book_id         int not null
        references Books (book_id),
    issue_date      DATE,
    debt_amount     DECIMAl
);

create table if not exists BookReservations
(
    reservation_id      serial primary key,
    name                varchar(50) not null,
    book_id             int not null
        references Books (book_id),
    reader_id           int not null
        references Readers (reader_id),
    staff_id           int not null
        references LibraryStaff (staff_id),
    reservation_date    DATE
);

create table if not exists Ratings
(
    rate_id      serial primary key,
    book_id             int not null
        references Books (book_id),
    reader_id           int not null
        references Readers (reader_id),
    rate_date           DATE,
    rate_amount         int not null,
    rate_text           text
);

CREATE INDEX idx_books_name ON Books(name);
CREATE INDEX idx_books_author_id ON Books(author_id);
CREATE INDEX idx_books_genre_id ON Books(genre_id);
CREATE INDEX idx_authors_name ON Authors(name);
CREATE INDEX idx_publishers_name ON Publishers(name);
CREATE INDEX idx_genres_name ON Genres(name);
CREATE INDEX idx_readers_name ON Readers(name);
CREATE INDEX idx_readers_reader_number ON Readers(reader_number);
CREATE INDEX idx_book_loans_reader_id ON BookLoans(reader_id);
CREATE INDEX idx_book_loans_book_id ON BookLoans(book_id);
CREATE INDEX idx_book_reservations_reader_id ON BookReservations(reader_id);
CREATE INDEX idx_book_reservations_book_id ON BookReservations(book_id);
CREATE INDEX idx_penalties_reader_id ON Penalties(reader_id);
CREATE INDEX idx_ratings_book_id ON Ratings(book_id);
CREATE INDEX idx_ratings_reader_id ON Ratings(reader_id);
