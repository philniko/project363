# SOEN363 Group Project - Databases

Welcome to the SOEN363 group project repository! This project is focused on implementing and querying a database system for our coursework in SOEN363.

## Team Members
We are a team of four members working on this project:

- **Adam Tahle**: 40237870 (adamtahle7@gmail.com)
- **Philippe Nikolov**: 40245641 (philippe.nikolov@outlook.com)
- **Adam Oughourlian**: 40246313 (adamoughourlian@hotmail.com)
- **Peter Torbey**: 40246387 (ptorbey242@gmail.com)

---

## Implementation Guide
Follow the steps below to set up and run the project on your local system:

### **1. Prerequisites**
- Install **pgAdmin** (PostgreSQL database management tool).
- Install an **IDE for Python** (e.g., **VSCode** is recommended).

### **2. Clone the Repository**
Using Git Bash, clone the repository onto your system:
```bash
git clone <repository_url>
```

### **3. Configure the Python Script**
- Open the Python script (`script.py`) in your IDE.
- Locate the database configuration section (`DB_CONFIG`).
- Adjust the `password` field to match your **pgAdmin** password:
```python
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "**your_pgadmin_password**",
    "host": "localhost",
    "port": 5432
}
```

### **4. Set Up the Database**
- Open **pgAdmin** and create a new database.
- Open the `dbcreation.sql` file and copy its content.
- Paste the SQL code into the **Query Tool** of your newly created database in pgAdmin.
- Execute the query to create the required tables and constraints.

### **5. Run the Python Script**
- In your terminal or IDE, run the Python script to populate the database with data:
```bash
python script.py
```
- Follow any prompts or instructions that appear during execution.

### **6. Execute SQL Queries**
- Open the `QueryImplementation.sql` file.
- Copy-paste the queries into the **Query Tool** of pgAdmin.
- Execute the queries to view the results and validate the database functionality.

---

## Repository Structure
- `script.py`: Python script for populating the database using external data sources.
- `dbcreation.sql`: SQL file containing the commands to create the database schema.
- `Query Implementation.sql`: SQL file with various queries for testing and implementation.
- `erd.png`: Image of the ERD of the database.

---

If you encounter any issues, please feel free to reach out to the team for assistance!
