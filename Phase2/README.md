# Phase 2: Database Migration

In Phase 2, we migrated data from PostgreSQL to MongoDB to handle a **large dataset** more flexibly and efficiently. This transition allows for faster queries and supports modern NoSQL-based workflows.

---

## Migration Overview

We migrated three main datasets: **Genres**, **Authors**, and **Books**. The migration process included extracting data from PostgreSQL, transforming it for MongoDB, and embedding relationships for efficient querying.

### 1. Genres
- Extracted `genre_id` and `name` from PostgreSQL.
- Migrated to the `genres` collection in MongoDB.
- Each genre uses `genre_id` as its `_id`.

### 2. Authors
- Extracted `author_id` and `name` from PostgreSQL.
- Migrated to the `authors` collection in MongoDB.
- Each author uses `author_id` as its `_id`.

### 3. Books
- Extracted book details along with related authors and genres using SQL joins.
- Embedded `authors` and `genres` directly into the `books` collection for fast, single-query access.
- Inserted in batches of 1,000 for optimal performance.

---

## Key Benefits

- **Simplified Queries**: Embedded relationships reduce the need for additional lookups.
- **Scalable Design**: MongoDB's document-oriented structure supports large datasets.
- **Efficient Performance**: Batch processing and optimized schema improve query speeds.

---

## Implementation Guide

### Prerequisites
1. **Database Connections**:
   - PostgreSQL: Ensure access to the database with necessary credentials.
   - MongoDB: Have a running MongoDB instance (local or cloud).

2. **Libraries**:
   - Install required Python libraries:
     ```bash
     pip install psycopg2 pymongo
     ```

3. **Configuration**:
   - Update database credentials and connection details in the script.

### Steps

1. **Set Up PostgreSQL Connection**:
   - Open the python script (`modified_script.py`)
   - Locate the database configuration section (`pg_conn`)
   - Adjust the `password` field to match your pgAdming password:
     ```python
     pg_conn = psycopg2.connect(
         dbname="postgres",
         user="postgres",
         password="your_pgadmin_password",
         host="localhost",
         port="5432"
     )
     ```


2. Setup Up the Database
- Open pgAdmin and create a new database.
- Open the `modified_dbcreation.sql` file and copy its content.
- Paste the SQL code into the Query Tool of your newly created database in pgAdmin.
- Execute the query to create the required tables and constraints.

3. Run the SQL DB population python script
- In your terminal, run the `modified_script.py` file to populate the database, as many times as desired. It randomly selects queries to assure new books are found and added.
```
python modified_script.py
```

4. Set Up MongoDb Connection:
- In `mongoscript.py`, set the connection
- Default connection setup:
```python
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["your_mongo_db"]
```

4. Run the mongo migration python script
- In your terminal, run the `mongoscript.py` file to migrate the data from the SQL database to your mongo database.
```bash
python mongoscript.py
```

---

This guide ensures a smooth migration process, transforming relational data into a document-oriented model for efficient MongoDB queries.
