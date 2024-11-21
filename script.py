import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import time

# Google Books API Key
API_KEY = "AIzaSyDgjYHqDU_HReneinncfPpsFAfAIe_JbHw"

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "docker",
    "host": "localhost",
    "port": 5432,
}

# Function to fetch books from Google Books API
def fetch_books(query, max_results=40, start_index=0):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}&maxResults={min(max_results, 40)}&startIndex={start_index}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error fetching books: {response.status_code}, {response.text}")
        return []


def parse_published_date(date_str):
    if not date_str:
        return None
    formats = ['%Y-%m-%d', '%Y-%m', '%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None  # Return None if no format matches


# Function to insert books into PostgreSQL database
def insert_books_to_db(books):
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Preparing the data for bulk insertion
        book_data = [
            (
                book.get("title"),
                book.get("authors"),
                book.get("published_date"),
                book.get("description"),
                book.get("average_rating"),
                book.get("ratings_count"),
                book.get("genres"),
                book.get("page_count"),
                book.get("language"),
                book.get("isbn_13"),  # Include ISBN-13 in the data tuple
            )
            for book in books
        ]
        
        # SQL for inserting book data
        insert_query = """
            INSERT INTO books (
                title, authors, published_date, description, average_rating, ratings_count, genres, page_count, language, isbn_13
            ) VALUES %s
        """
        
        # Using execute_values for bulk insert
        execute_values(cursor, insert_query, book_data)
        connection.commit()
        print(f"{len(books)} books inserted successfully!")
    except Exception as e:
        print(f"Error inserting books into database: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    search_query = input("Enter a search query (e.g., fiction, history): ").strip()
    total_books_to_fetch = 100 # Set the total number of books you want to fetch
    all_books = []
    start_index = 0
    books_per_request = 40  # Maximum allowed by the API

    print("Fetching books from Google Books API...")
    while len(all_books) < total_books_to_fetch:
        books_to_fetch = min(books_per_request, total_books_to_fetch - len(all_books))
        raw_books = fetch_books(search_query, max_results=books_to_fetch, start_index=start_index)
        if not raw_books:
            print("No more books available or an error occurred.")
            break
        all_books.extend(raw_books)
        start_index += books_per_request
        time.sleep(1)  # Be polite to the API

    print(f"Processing {len(all_books)} books...")
    processed_books = []
    for item in all_books:
        volume_info = item.get("volumeInfo", {})
        # Extract ISBN-13
        isbn_13 = None
        industry_identifiers = volume_info.get("industryIdentifiers", [])
        for identifier in industry_identifiers:
            if identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier")
                break  # Exit the loop once ISBN-13 is found
        processed_books.append({
            "title": volume_info.get("title"),
            "authors": volume_info.get("authors", []),
            "published_date": parse_published_date(volume_info.get("publishedDate")),
            "description": volume_info.get("description"),
            "average_rating": volume_info.get("averageRating"),
            "ratings_count": volume_info.get("ratingsCount"),
            "genres": volume_info.get("categories", []),
            "page_count": volume_info.get("pageCount"),
            "language": volume_info.get("language"),
            "isbn_13": isbn_13,  # Include ISBN-13 in the processed data
        })

    print("Inserting books into the database...")
    insert_books_to_db(processed_books)