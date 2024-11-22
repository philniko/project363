-- ============================================
--            Database Creation Script
-- ============================================

-- ---------------------------
-- Custom Domains and Types
-- ---------------------------

-- ISBN-13 domain
CREATE DOMAIN isbn13 AS VARCHAR(13)
  CHECK (VALUE ~ '^\d{13}$');

-- Language code domain (2 lowercase letters)
CREATE DOMAIN language_code AS VARCHAR(2)
  CHECK (VALUE ~ '^[a-z]{2}$');

-- Rating domain (between 0 and 5)
CREATE DOMAIN rating AS NUMERIC(2,1)
  CHECK (VALUE >= 0 AND VALUE <= 5);

-- Valid date domain (not in the future)
CREATE DOMAIN valid_date AS DATE
  CHECK (VALUE <= CURRENT_DATE);

-- ---------------------------
-- Publications Table
-- ---------------------------

-- Stores general publication information
CREATE TABLE Publications (
    publication_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    language language_code,
    google_books_id VARCHAR(50),
    open_library_id VARCHAR(50)
);

-- ---------------------------
-- Books Table (IS-A Publications)
-- ---------------------------

-- Inherits from Publications via shared primary key
CREATE TABLE Books (
    publication_id INTEGER PRIMARY KEY,
    average_rating rating,
    ratings_count INTEGER,
    FOREIGN KEY (publication_id) REFERENCES Publications(publication_id)
);

-- ---------------------------
-- Editions Table (Weak Entity)
-- ---------------------------

-- Stores edition-specific information
CREATE TABLE Editions (
    edition_id SERIAL PRIMARY KEY,
    publication_id INTEGER NOT NULL REFERENCES Publications(publication_id),
    open_library_id VARCHAR(50) UNIQUE,
    isbn_13 isbn13,
    published_date valid_date,
    page_count INTEGER
);

-- ---------------------------
-- Authors Table
-- ---------------------------

-- Stores author information
CREATE TABLE Authors (
    author_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    date_of_birth valid_date,
    biography TEXT
);

-- ---------------------------
-- BookAuthors Table (Associative Entity)
-- ---------------------------

-- Links books and authors (many-to-many relationship)
CREATE TABLE BookAuthors (
    publication_id INTEGER REFERENCES Publications(publication_id),
    author_id INTEGER REFERENCES Authors(author_id),
    PRIMARY KEY (publication_id, author_id)
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
-- BookGenres Table (Associative Entity)
-- ---------------------------

-- Links books and genres (many-to-many relationship)
CREATE TABLE BookGenres (
    publication_id INTEGER REFERENCES Publications(publication_id),
    genre_id INTEGER REFERENCES Genres(genre_id),
    PRIMARY KEY (publication_id, genre_id)
);

-- ---------------------------
-- Trigger Function for Complex Referential Integrity
-- ---------------------------

-- Ensures an author's date of birth is before any of their book's published dates
CREATE OR REPLACE FUNCTION check_author_birth_date()
RETURNS TRIGGER AS $$
DECLARE
    author_birth_date DATE;
BEGIN
    SELECT MIN(a.date_of_birth) INTO author_birth_date
    FROM Authors a
    JOIN BookAuthors ba ON a.author_id = ba.author_id
    WHERE ba.publication_id = NEW.publication_id;

    IF NEW.published_date IS NOT NULL AND author_birth_date IS NOT NULL AND NEW.published_date < author_birth_date THEN
        RAISE EXCEPTION 'Published date cannot be before author''s date of birth';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the Editions table
CREATE TRIGGER trigger_check_author_birth_date
BEFORE INSERT OR UPDATE ON Editions
FOR EACH ROW
EXECUTE PROCEDURE check_author_birth_date();

-- ---------------------------
-- Views for User Access Rights
-- ---------------------------

-- Low access view (limited data)
CREATE VIEW low_access_books AS
SELECT
    p.title,
    a.name AS author_name
FROM Publications p
JOIN BookAuthors ba ON p.publication_id = ba.publication_id
JOIN Authors a ON ba.author_id = a.author_id;

-- Full access view (complete data)
CREATE VIEW full_access_books AS
SELECT
    p.publication_id,
    p.title,
    p.description,
    p.language,
    p.google_books_id,
    p.open_library_id,
    b.average_rating,
    b.ratings_count,
    e.edition_id,
    e.isbn_13,
    e.published_date AS edition_published_date,
    e.page_count,
    a.author_id,
    a.name AS author_name,
    a.date_of_birth,
    a.biography,
    g.genre_id,
    g.name AS genre_name
FROM Publications p
JOIN Books b ON p.publication_id = b.publication_id
LEFT JOIN Editions e ON p.publication_id = e.publication_id
LEFT JOIN BookAuthors ba ON p.publication_id = ba.publication_id
LEFT JOIN Authors a ON ba.author_id = a.author_id
LEFT JOIN BookGenres bg ON p.publication_id = bg.publication_id
LEFT JOIN Genres g ON bg.genre_id = g.genre_id;

-- ============================================
--              End of Script
-- ============================================
