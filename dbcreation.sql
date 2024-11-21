CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn_13 VARCHAR(13),
    title TEXT NOT NULL,
    authors TEXT[],
    published_date DATE,
    description TEXT,
    average_rating NUMERIC,
    ratings_count INTEGER,
    genres TEXT[],
    page_count INTEGER,
    language TEXT
);
