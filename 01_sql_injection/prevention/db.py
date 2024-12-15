import re
import sqlite3

# SQL Injection Detection Patterns
SQLI_PATTERNS = [
    r"(?i)union",  # UNION keyword
    r"(?i)select.*from",  # SELECT * FROM
    r"(?i)insert\s+into",  # INSERT INTO
    r"(?i)update.*set",  # UPDATE table SET
    r"(?i)delete\s+from",  # DELETE FROM
    r"(?i)drop\s+table",  # DROP TABLE
    r"--",  # Comment marker
    r";",  # Semicolon for chaining queries
]

# Allowed Queries for Whitelisting
ALLOWED_QUERIES = [
    "SELECT * FROM voters WHERE voter_id = ?",
    "SELECT * FROM admins WHERE username = ? AND password = ?",
]


def log_attack(detection_layer, blocking_layer, query, reason):
    print(f"\n[SECURITY ALERT] SQL Injection detected!")
    print(f"  - Detected at: {detection_layer}")
    print(f"  - Blocked by: {blocking_layer}")
    print(f"  - Query: {query}")
    print(f"  - Reason: {reason}\n")


def validate_input(input_data):
    # Layer 1: Input Validation
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, input_data):
            return False, f"Pattern matched: {pattern}"
    return True, None


def normalize_input(input_data):
    # Layer 2: Input Normalization
    return input_data.strip().replace("\t", "").replace("\n", "")


def execute_query(query, params=None):
    # Layer 3: Query Whitelisting
    if query not in ALLOWED_QUERIES:
        log_attack("Query Whitelisting", "Query Whitelisting", query, "Query not in allowed list.")
        raise Exception("Blocked due to query not in allowed list.")

    # Database connection
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    try:
        # Layer 4: Parameterized Query Execution
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Log the query execution
        print(f"[INFO] Executed query: {query}")

        results = cursor.fetchall()
        conn.commit()
        return results

    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        raise

    finally:
        conn.close()


def initialize_db():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS voters")
    cursor.execute("DROP TABLE IF EXISTS admins")

    # Create tables
    cursor.execute('''
        CREATE TABLE voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            voter_id TEXT UNIQUE NOT NULL,
            vote_casted TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Insert sample data
    voter_data = [
        ('Alice Johnson', 'V101', 'Candidate A'),
        ('Bob Smith', 'V102', 'Candidate B'),
        ('Charlie Davis', 'V103', 'Candidate A'),
        ('Diana Evans', 'V104', 'Candidate C'),
        ('Ethan Brown', 'V105', 'Candidate B'),
    ]
    admin_data = [
        ('admin', 'admin123'),
        ('superuser', 'supersecret'),
    ]

    cursor.executemany("INSERT INTO voters (name, voter_id, vote_casted) VALUES (?, ?, ?)", voter_data)
    cursor.executemany("INSERT INTO admins (username, password) VALUES (?, ?)", admin_data)

    conn.commit()
    conn.close()
