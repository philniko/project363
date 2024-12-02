-- ---------------------------
-- Books Table
-- ---------------------------

-- Combines publication and book information
CREATE TABLE Books (
    book_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    language VARCHAR(10),  -- No domain, just a plain VARCHAR
    google_books_id VARCHAR(50) UNIQUE,
    open_library_id VARCHAR(50) UNIQUE,
    average_rating NUMERIC(2, 1),  -- Plain numeric for simplicity
    ratings_count INTEGER,
    isbn_13 VARCHAR(13),  -- No domain, just a plain VARCHAR
    published_date DATE,
    page_count INTEGER
);

-- ---------------------------
-- Authors Table
-- ---------------------------

-- Stores author information
CREATE TABLE Authors (
    author_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- Avoid duplicate authors
    date_of_birth DATE,
    biography TEXT
);

-- ---------------------------
-- BookAuthors Table
-- ---------------------------

-- Links books and authors (many-to-many relationship)
CREATE TABLE BookAuthors (
    book_id INTEGER REFERENCES Books(book_id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES Authors(author_id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

-- ---------------------------
-- Genres Table
-- ---------------------------

-- Stores genre information
CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- ---------------------------
-- BookGenres Table
-- ---------------------------

-- Links books and genres (many-to-many relationship)
CREATE TABLE BookGenres (
    book_id INTEGER REFERENCES Books(book_id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES Genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);
