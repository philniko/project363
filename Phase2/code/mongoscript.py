import psycopg2
from pymongo import MongoClient

# Configuration
BATCH_SIZE = 1000  # Number of rows to process in each batch

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="docker",
    host="localhost",
    port="5432"
)
pg_cursor = pg_conn.cursor()

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["your_mongo_db"]
books_collection = mongo_db["books"]
authors_collection = mongo_db["authors"]
genres_collection = mongo_db["genres"]

# Migrate Genres Table
pg_cursor.execute("SELECT genre_id, name FROM Genres")
genres = []
for row in pg_cursor.fetchall():
    genre_document = {
        "_id": row[0],  # Use genre_id as _id
        "name": row[1]
    }
    genres.append(genre_document)
genres_collection.insert_many(genres)
print("Migrated Genres table.")

# Migrate Authors Table
pg_cursor.execute(
    "SELECT author_id, name FROM Authors")
authors = []
for row in pg_cursor.fetchall():
    author_document = {
        "_id": row[0],  # Use author_id as _id
        "name": row[1]
    }
    authors.append(author_document)
authors_collection.insert_many(authors)
print("Migrated Authors table.")

# Migrate Books with Relationships (Authors and Genres)
pg_cursor.execute("""
    SELECT 
        b.book_id,
        b.title,
        b.description,
        b.language,
        b.google_books_id,
        b.open_library_id,
        b.average_rating,
        b.ratings_count,
        b.isbn_13,
        b.published_date,
        b.page_count,
        ARRAY_AGG(DISTINCT jsonb_build_object('author_id', a.author_id, 'name', a.name)) AS authors,
        ARRAY_AGG(DISTINCT jsonb_build_object('genre_id', g.genre_id, 'name', g.name)) AS genres
    FROM books b
    LEFT JOIN bookauthors ba ON b.book_id = ba.book_id
    LEFT JOIN authors a ON ba.author_id = a.author_id
    LEFT JOIN bookgenres bg ON b.book_id = bg.book_id
    LEFT JOIN genres g ON bg.genre_id = g.genre_id
    GROUP BY b.book_id
""")
books = []
while True:
    rows = pg_cursor.fetchmany(BATCH_SIZE)
    if not rows:
        break

    for row in rows:
        book_document = {
            "_id": row[0],  # Use book_id as _id
            "title": row[1],
            "description": row[2],
            "language": row[3],
            "google_books_id": row[4],
            "open_library_id": row[5],
            "average_rating": float(row[6]) if row[6] else None,
            "ratings_count": row[7],
            "isbn_13": row[8],
            "published_date": row[9].isoformat() if row[9] else None,
            "page_count": row[10],
            "authors": row[11] or [],
            "genres": row[12] or []
        }
        books.append(book_document)

    # Insert batch of books into MongoDB
    books_collection.insert_many(books)
    print(f"Migrated {len(books)} books.")
    books = []  # Clear batch for the next iteration

print("Migrated Books table.")

# Close connections
pg_cursor.close()
pg_conn.close()
mongo_client.close()
