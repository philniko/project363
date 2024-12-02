import random
import string
import time
import requests
import psycopg2
from datetime import date
from dateutil import parser
from tqdm import tqdm

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "docker",
    "host": "localhost",
    "port": 5432,
}


def fetch_books(query, max_results=40, start_index=0):
    API_KEY = "AIzaSyDAlis52XgUl6kC3iw-yqY8WnmTUn6Um_0"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}&maxResults={max_results}&startIndex={start_index}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        tqdm.write(
            f"Error fetching books: {response.status_code}, {response.text}")
        return []


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return parser.parse(date_str, fuzzy=True).date()
    except (ValueError, OverflowError, TypeError):
        return None


def insert_books_to_db(books):
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    author_cache = {}
    genre_cache = {}

    for book in tqdm(books, desc="Inserting books"):
        # Insert into Books
        cursor.execute("""
            INSERT INTO Books (title, description, language, google_books_id, average_rating, ratings_count, isbn_13, published_date, page_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (google_books_id) DO NOTHING
            RETURNING book_id
        """, (
            book["title"], book["description"], book["language"], book["google_books_id"],
            book["average_rating"], book["ratings_count"], book["isbn_13"],
            book["published_date"], book["page_count"]
        ))
        result = cursor.fetchone()
        if result:
            book_id = result[0]
        else:
            # Fetch existing book_id if it already exists
            cursor.execute(
                "SELECT book_id FROM Books WHERE google_books_id = %s", (book["google_books_id"],))
            book_id = cursor.fetchone()[0]

        # Insert Authors
        for author_name in book["authors"]:
            if author_name not in author_cache:
                cursor.execute("""
                    INSERT INTO Authors (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING author_id
                """, (author_name,))
                result = cursor.fetchone()
                if result:
                    author_id = result[0]
                else:
                    cursor.execute(
                        "SELECT author_id FROM Authors WHERE name = %s", (author_name,))
                    author_id = cursor.fetchone()[0]
                author_cache[author_name] = author_id
            else:
                author_id = author_cache[author_name]

            cursor.execute("""
                INSERT INTO BookAuthors (book_id, author_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (book_id, author_id))

        # Insert Genres
        for genre_name in book["genres"]:
            if genre_name not in genre_cache:
                cursor.execute("""
                    INSERT INTO Genres (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING genre_id
                """, (genre_name,))
                result = cursor.fetchone()
                if result:
                    genre_id = result[0]
                else:
                    cursor.execute(
                        "SELECT genre_id FROM Genres WHERE name = %s", (genre_name,))
                    genre_id = cursor.fetchone()[0]
                genre_cache[genre_name] = genre_id
            else:
                genre_id = genre_cache[genre_name]

            cursor.execute("""
                INSERT INTO BookGenres (book_id, genre_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (book_id, genre_id))

    connection.commit()
    connection.close()


def generate_random_queries(base_terms, num_variations=20):
    """Generate random queries by appending random characters to base terms."""
    return [f"{term} {random.choice(string.ascii_lowercase)}" for term in base_terms for _ in range(num_variations)]


if __name__ == "__main__":
    base_terms = [
        "fiction", "nonfiction", "dragon", "magic", "science", "history",
        "adventure", "war", "hero", "legend", "myth", "fantasy", "romance",
        "horror", "biography", "school", "travel", "philosophy", "art", "technology"
    ]

    # Generate a large list of diverse queries
    random_queries = generate_random_queries(base_terms, num_variations=20)
    static_queries = [
        "intitle:adventure", "intitle:love", "intitle:war", "intitle:peace",
        "subject:fiction", "subject:history", "subject:science", "subject:biography",
        "inauthor:rowling", "inauthor:tolkien", "inauthor:asimov", "inauthor:shakespeare"
    ]
    subqueries = static_queries + random_queries

    # Fetch and process books
    total_books_to_fetch = 40000  # Total books desired
    books_per_query = 1000  # Max per query
    batch_size = 40  # Number of books per request
    all_books = []
    seen_ids = set()

    for subquery in tqdm(subqueries, desc="Fetching books by subquery"):
        start_index = 0
        while len(all_books) < total_books_to_fetch and start_index < books_per_query:
            raw_books = fetch_books(
                subquery, max_results=batch_size, start_index=start_index)
            if not raw_books:
                break
            for item in raw_books:
                volume_info = item.get("volumeInfo", {})

                # Skip books with missing essential fields or duplicates
                google_books_id = item.get("id")
                if not volume_info.get("title") or not volume_info.get("authors") or google_books_id in seen_ids:
                    continue

                seen_ids.add(google_books_id)

                all_books.append({
                    "title": volume_info.get("title"),
                    "description": volume_info.get("description") or "No description available",
                    "language": volume_info.get("language"),
                    "google_books_id": google_books_id,
                    "average_rating": volume_info.get("averageRating"),
                    "ratings_count": volume_info.get("ratingsCount"),
                    "isbn_13": next((id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"), None),
                    "published_date": parse_date(volume_info.get("publishedDate")),
                    "page_count": volume_info.get("pageCount"),
                    "authors": volume_info.get("authors", []),
                    "genres": volume_info.get("categories", [])
                })

            start_index += batch_size
            time.sleep(1)

        if len(all_books) >= total_books_to_fetch:
            break

    tqdm.write(f"Total books fetched: {len(all_books)}")
    tqdm.write("Inserting books into the database...")
    insert_books_to_db(all_books)
