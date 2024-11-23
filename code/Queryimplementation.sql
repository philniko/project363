-- ============================================
--            Database Implementation Script
-- This code will answer all query questions from the Query implementation part in project phase I
-- ============================================



-- 1. Query that retrieve the titles and descriptions of all publications where the average rating is greater than 4
SELECT 
    p.title, 
    p.description 
FROM 
    publications p
JOIN 
    books b 
ON 
    p.publication_id = b.publication_id
WHERE 
    b.average_rating > 4;


-- 2.1 Query that groups books by their language and count how many books exist for each language

--  *WITHOUT HAVING CLAUSE*
SELECT 
    p.language, 
    COUNT(b.publication_id) AS book_count
FROM 
    publications p
JOIN 
    books b 
ON 
    p.publication_id = b.publication_id
GROUP BY 
    p.language;

-- 2.2 Query that groups books by their language and show only languages with more than 5 books
-- *WITH HAVING CLAUSE*
SELECT 
    p.language, 
    COUNT(b.publication_id) AS book_count
FROM 
    publications p
JOIN 
    books b 
ON 
    p.publication_id = b.publication_id
GROUP BY 
    p.language
HAVING 
    COUNT(b.publication_id) > 5;


-- 3.1 Query that retrieves the titles of publications along with the names of their authors
-- *USING SIMPLE JOIN*
SELECT 
    p.title, 
    a.name AS author_name
FROM 
    publications p
JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id
JOIN 
    authors a 
ON 
    ba.author_id = a.author_id;

-- *USING CARTESIONS PRODUCT WITH WHERE CLAUSE*
SELECT 
    p.title, 
    a.name AS author_name
FROM 
    publications p, 
    bookauthors ba, 
    authors a
WHERE 
    p.publication_id = ba.publication_id 
    AND ba.author_id = a.author_id;


-- 4.1 Query that retrieves all publications that have associated authors
-- *USING INNER JOIN*
SELECT 
    p.title, 
    ba.author_id
FROM 
    publications p
INNER JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id;

-- 4.2 Query that retrives all publications including those without authors
-- *USING LEFT OUTER JOIN*
SELECT 
    p.title, 
    ba.author_id
FROM 
    publications p
LEFT JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id;

-- 4.3 Query that retrieves all authors including those who haven't written a publication
-- *USING RIGHT OUTER JOIN*
SELECT 
    p.title, 
    ba.author_id
FROM 
    publications p
RIGHT JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id;

-- 4.4 Query that retrieves all publications and authors wether they are associated or not
-- *USING FULL OUTER JOIN*
SELECT 
    p.title, 
    ba.author_id
FROM 
    publications p
FULL JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id;


-- 5.1 Query that retrieves all publications where the description field is NULL (no description available)
SELECT 
    title, 
    description 
FROM 
    publications
WHERE 
    description IS NULL;

-- 5.2 Query that retrieves all publications and replace NULL in the description field with "No Description Available"
SELECT 
    title, 
    COALESCE(description, 'No Description Available') AS description
FROM 
    publications;

-- 5.3 Query that retrieves all books that have a defined average rating (exclude NULL ratings)
SELECT 
    p.title, 
    b.average_rating
FROM 
    publications p
JOIN 
    books b 
ON 
    p.publication_id = b.publication_id
WHERE 
    b.average_rating IS NOT NULL;

-- 5.4 Query that counts how many publications lack a defined description
SELECT 
    COUNT(*) AS null_description_count
FROM 
    publications
WHERE 
    description IS NULL;

-- 5.5 Query that calculates the average rating for books, ignoring NULL values in the average_rating column
SELECT 
    AVG(average_rating) AS average_rating
FROM 
    books;

-- 5.6 Query that retrieves all publications, showing NULL values for authors where no authors are associated
SELECT 
    p.title, 
    ba.author_id
FROM 
    publications p
LEFT JOIN 
    bookauthors ba 
ON 
    p.publication_id = ba.publication_id;


-- 6.1 Query that Retrieve the titles of publications that have a higher average rating than the average rating of all books
SELECT 
    p.title
FROM 
    publications p
JOIN 
    books b 
ON 
    p.publication_id = b.publication_id
WHERE 
    b.average_rating > (
        SELECT 
            AVG(average_rating)
        FROM 
            books
    );

-- 6.2 Query that retrieves the names of authors who have written the maximum number of publications
SELECT 
    a.name
FROM 
    authors a
WHERE 
    (SELECT 
         COUNT(*)
     FROM 
         bookauthors ba
     WHERE 
         ba.author_id = a.author_id
    ) = (
        SELECT 
            MAX(author_count)
        FROM 
            (
                SELECT 
                    ba.author_id, 
                    COUNT(*) AS author_count
                FROM 
                    bookauthors ba
                GROUP BY 
                    ba.author_id
            ) subquery
    );


-- 7.1 Query that retrieves the titles of publications that exist in both publications and books
-- *USING INTERSECT*
SELECT title
FROM publications
INTERSECT
SELECT title
FROM books;

-- *WITHOUT USING ANY SET OPERATION*
SELECT p.title
FROM publications p
JOIN books b
ON p.title = b.title;

-- 7.2 Query that retrieves all unique publication titles from both publications and books
-- *USING UNION*
SELECT title
FROM publications
UNION
SELECT title
FROM books;

-- *WITHOUT USING ANY SET OPERATION*
SELECT DISTINCT title
FROM (
    SELECT title FROM publications
    UNION ALL
    SELECT title FROM books
) subquery;

-- 7.3 Query that retrieves the titles of publications that exist in publications but not in books
-- *USING EXCEPT*
SELECT title
FROM publications
EXCEPT
SELECT title
FROM books;

-- *WITHOUT USING ANY SET OPERATION*
SELECT title
FROM publications
WHERE title NOT IN (
    SELECT title
    FROM books
);


-- 8. Query that has a view that filters data based on a hard-coded genre_ID of 5
-- Create
CREATE VIEW sci_fi_books AS
SELECT 
    p.title, 
    g.name AS genre
FROM 
    publications p
JOIN 
    bookgenres bg 
ON 
    p.publication_id = bg.publication_id
JOIN 
    genres g 
ON 
    bg.genre_id = g.genre_id
WHERE 
    g.genre_id = 5;

-- Modify
CREATE OR REPLACE VIEW sci_fi_books AS
SELECT 
    p.title, 
    g.name AS genre
FROM 
    publications p
JOIN 
    bookgenres bg 
ON 
    p.publication_id = bg.publication_id
JOIN 
    genres g 
ON 
    bg.genre_id = g.genre_id
WHERE 
    g.genre_id = 10; -- Updated hard-coded value


-- 9.1 Query that finds the publications that appear in both full_access_books and low_access_books
-- *USING OVERLAP CONSTRAINT*
SELECT 
    fab.publication_id, 
    fab.title
FROM 
    full_access_books fab
JOIN 
    low_access_books lab 
ON 
    fab.title = lab.title AND fab.author_name = lab.author_name;

-- 9.2 Query that finds publications that do not belong to either full_access_books or low_access_books
-- *USING COVERING CONSTRAINT*
SELECT 
    p.publication_id, 
    p.title
FROM 
    publications p
LEFT JOIN 
    full_access_books fab 
ON 
    p.title = fab.title
LEFT JOIN 
    low_access_books lab 
ON 
    p.title = lab.title
WHERE 
    fab.publication_id IS NULL 
    AND lab.title IS NULL;


-- 10. Queries that find books that belong to all genres in a specific list
-- *USING NOT IN*
SELECT DISTINCT b.publication_id
FROM books b
WHERE NOT EXISTS (
    SELECT g.genre_id
    FROM genres g
    WHERE g.genre_id NOT IN (
        SELECT bg.genre_id
        FROM bookgenres bg
        WHERE bg.publication_id = b.publication_id
    )
);

-- *USING NOT EXISTS*
SELECT DISTINCT b.publication_id
FROM books b
WHERE NOT EXISTS (
    SELECT g.genre_id
    FROM genres g
    WHERE NOT EXISTS (
        SELECT bg.genre_id
        FROM bookgenres bg
        WHERE bg.genre_id = g.genre_id AND bg.publication_id = b.publication_id
    )
);

-- *USING EXCEPT*
SELECT DISTINCT b.publication_id
FROM books b
WHERE NOT EXISTS (
    SELECT genre_id
    FROM genres
    EXCEPT
    SELECT bg.genre_id
    FROM bookgenres bg
    WHERE bg.publication_id = b.publication_id
);
