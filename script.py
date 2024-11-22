import requests
import psycopg2
from datetime import datetime, date
import time
from dateutil import parser
from urllib.parse import urljoin
from tqdm import tqdm

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "docker",
    "host": "localhost",
    "port": 5432,
}

def fetch_books(query, max_results=40, start_index=0):
    API_KEY = "AIzaSyDgjYHqDU_HReneinncfPpsFAfAIe_JbHw"  # Replace with your actual API key
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}&maxResults={min(max_results, 40)}&startIndex={start_index}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        tqdm.write(f"Fetched {len(items)} books from Google Books API.")
        return items
    else:
        tqdm.write(f"Error fetching books: {response.status_code}, {response.text}")
        return []

def parse_date(date_str):
    if not date_str:
        return None
    try:
        parsed_date = parser.parse(date_str, fuzzy=True).date()
        if parsed_date > date.today():
            return None  # Invalid future date
        return parsed_date
    except (ValueError, OverflowError, TypeError):
        return None

def fetch_author_data(author_name):
    try:
        search_url = f"https://openlibrary.org/search/authors.json?q={author_name}"
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return {'name': author_name, 'birth_date': None, 'bio': None}
    
    if data.get('numFound', 0) > 0:
        author_info = data['docs'][0]
        author_key = author_info.get('key')  # e.g., '/authors/OL2821271A' or 'OL2821271A'
        birth_date_str = author_info.get('birth_date')
        parsed_birth_date = parse_date(birth_date_str)
        if author_key:
            # Extract author ID from author_key
            author_id = author_key.split('/')[-1]
            author_detail_url = f"https://openlibrary.org/authors/{author_id}.json"
            try:
                detail_response = requests.get(author_detail_url)
                detail_response.raise_for_status()
                detail_data = detail_response.json()
                bio = detail_data.get('bio')
                if isinstance(bio, dict):
                    bio = bio.get('value')
                return {
                    'name': detail_data.get('name'),
                    'birth_date': parsed_birth_date,
                    'bio': bio
                }
            except requests.exceptions.RequestException:
                return {
                    'name': author_info.get('name'),
                    'birth_date': parsed_birth_date,
                    'bio': None
                }
    return {'name': author_name, 'birth_date': None, 'bio': None}

def fetch_open_library_data(isbn_13):
    if not isbn_13:
        return None
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_13}&format=json&jscmd=data"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    book_key = f"ISBN:{isbn_13}"
    book_data = data.get(book_key)
    if not book_data:
        return None
    open_library_id = book_data.get('key')  # e.g., '/books/OL7353617M'
    if open_library_id:
        open_library_id = open_library_id.split('/')[-1]
    else:
        return None
    return {
        'open_library_id': open_library_id,
        'published_date': parse_date(book_data.get('publish_date')),
        'page_count': book_data.get('number_of_pages')
    }

def insert_books_to_db(books):
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Cache to avoid duplicate authors and genres
        author_cache = {}
        genre_cache = {}

        for book in tqdm(books, desc="Inserting books"):
            # Insert into Publications
            cursor.execute("""
                INSERT INTO Publications (title, description, language, google_books_id)
                VALUES (%s, %s, %s, %s)
                RETURNING publication_id
            """, (
                book.get("title"),
                book.get("description"),
                book.get("language"),
                book.get("google_books_id")
            ))
            publication_id = cursor.fetchone()[0]

            # Insert into Books (IS-A Publications)
            average_rating = book.get("average_rating")
            if average_rating is not None and (average_rating < 0 or average_rating > 5):
                average_rating = None  # Ensure rating is between 0 and 5

            cursor.execute("""
                INSERT INTO Books (publication_id, average_rating, ratings_count)
                VALUES (%s, %s, %s)
            """, (
                publication_id,
                average_rating,
                book.get("ratings_count")
            ))

            # Handle authors
            for author_name in book.get("authors", []):
                if author_name not in author_cache:
                    # Fetch author data from Open Library API
                    author_data = fetch_author_data(author_name)
                    # Insert into Authors
                    cursor.execute("""
                        INSERT INTO Authors (name, date_of_birth, biography)
                        VALUES (%s, %s, %s)
                        RETURNING author_id
                    """, (
                        author_data.get("name"),
                        author_data.get("birth_date"),
                        author_data.get("bio"),
                    ))
                    author_id = cursor.fetchone()[0]
                    author_cache[author_name] = author_id
                else:
                    author_id = author_cache[author_name]

                # Insert into BookAuthors
                cursor.execute("""
                    INSERT INTO BookAuthors (publication_id, author_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (publication_id, author_id))

            # Handle Genres
            for genre_name in book.get("genres", []):
                if genre_name not in genre_cache:
                    # Insert genre if it doesn't exist
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
                        cursor.execute("SELECT genre_id FROM Genres WHERE name = %s", (genre_name,))
                        genre_id = cursor.fetchone()[0]
                    genre_cache[genre_name] = genre_id
                else:
                    genre_id = genre_cache[genre_name]
                # Insert into BookGenres
                cursor.execute("""
                    INSERT INTO BookGenres (publication_id, genre_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (publication_id, genre_id))

            # Fetch Open Library data
            open_library_data = fetch_open_library_data(book.get("isbn_13"))
            if open_library_data:
                open_lib_id = open_library_data.get('open_library_id')
                try:
                    cursor.execute("""
                        UPDATE Publications
                        SET open_library_id = %s
                        WHERE publication_id = %s
                    """, (
                        open_lib_id,
                        publication_id
                    ))
                    # Insert into Editions
                    cursor.execute("""
                        INSERT INTO Editions (publication_id, open_library_id, isbn_13, published_date, page_count)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (open_library_id) DO NOTHING
                    """, (
                        publication_id,
                        open_lib_id,
                        book.get('isbn_13'),
                        open_library_data.get('published_date'),
                        open_library_data.get('page_count'),
                    ))
                except Exception as e:
                    tqdm.write(f"Error updating or inserting edition for book '{book.get('title')}': {e}")
                    # Optionally, you can log the error or handle it as needed
            else:
                # Insert basic edition info if no Open Library data found
                try:
                    cursor.execute("""
                        INSERT INTO Editions (publication_id, isbn_13, published_date, page_count)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        publication_id,
                        book.get("isbn_13"),
                        book.get("published_date"),
                        book.get("page_count"),
                    ))
                except Exception as e:
                    tqdm.write(f"Error inserting basic edition for book '{book.get('title')}': {e}")
                    # Optionally, you can log the error or handle it as needed

        connection.commit()
        tqdm.write(f"{len(books)} books inserted successfully!")
    except Exception as e:
        tqdm.write(f"Error inserting books into database: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    search_query = input("Enter a search query (e.g., fiction, history): ").strip()
    total_books_to_fetch = 100  # Adjust as needed
    all_books = []
    start_index = 0
    books_per_request = 40

    tqdm.write("Fetching books from Google Books API...")
    while len(all_books) < total_books_to_fetch:
        books_to_fetch = min(books_per_request, total_books_to_fetch - len(all_books))
        raw_books = fetch_books(search_query, max_results=books_to_fetch, start_index=start_index)
        if not raw_books:
            tqdm.write("No more books available or an error occurred.")
            break
        all_books.extend(raw_books)
        start_index += books_per_request
        time.sleep(1)  # Respectful delay to avoid hitting API rate limits

    tqdm.write(f"Processing {len(all_books)} books...")
    processed_books = []
    for item in tqdm(all_books, desc="Processing books"):
        volume_info = item.get("volumeInfo", {})
        # Extract ISBN-13
        isbn_13 = None
        industry_identifiers = volume_info.get("industryIdentifiers", [])
        for identifier in industry_identifiers:
            if identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier")
                break
        # Ensure language code conforms to our domain (2 lowercase letters)
        language = volume_info.get("language")
        if language and len(language) == 2:
            language = language.lower()
        else:
            language = None

        # Ensure average_rating is between 0 and 5
        average_rating = volume_info.get("averageRating")
        if average_rating is not None:
            try:
                average_rating = float(average_rating)
                if average_rating < 0 or average_rating > 5:
                    average_rating = None
            except ValueError:
                average_rating = None

        processed_books.append({
            "title": volume_info.get("title"),
            "authors": volume_info.get("authors", []),
            "published_date": parse_date(volume_info.get("publishedDate")),
            "description": volume_info.get("description"),
            "average_rating": average_rating,
            "ratings_count": volume_info.get("ratingsCount"),
            "genres": volume_info.get("categories", []),
            "page_count": volume_info.get("pageCount"),
            "language": language,
            "isbn_13": isbn_13,
            "google_books_id": item.get("id"),
            "open_library_id": None  # Will be set later if available
        })

    tqdm.write("Inserting books into the database...")
    insert_books_to_db(processed_books)