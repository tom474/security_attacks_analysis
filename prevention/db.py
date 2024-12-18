import sqlite3
import os

DB_NAME = 'voting_system.db'
REPORTS_DIR = 'reports'
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'system.log')


# =========================
# Database Initialization
# =========================
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Drop and recreate tables
    print("[INFO] Dropping and recreating tables...")

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS voters")
    cursor.execute("DROP TABLE IF EXISTS admins")
    cursor.execute("DROP TABLE IF EXISTS candidates")
    cursor.execute("DROP TABLE IF EXISTS votes")

    # Create Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Voters table
    cursor.execute('''
        CREATE TABLE voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            voter_id TEXT UNIQUE NOT NULL,
            vote_casted TEXT NOT NULL
        )
    ''')

    # Create Candidates table
    cursor.execute('''
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')

    # Create Votes table
    cursor.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT NOT NULL,
            candidate TEXT NOT NULL
        )
    ''')

    # Insert mock data
    print("[INFO] Inserting sample data into tables...")

    # Users Table (Admins and Voters)
    user_data = [
        ('admin', 'admin123'),
        ('superuser', 'supersecret'),
    ]

    # Voter Table
    voter_data = [
        ('Alice Johnson', 'V101', 'Alice'),
        ('Bob Smith', 'V102', 'Bob'),
        ('Charlie Davis', 'V103', 'Alice'),
        ('Diana Evans', 'V104', 'Charlie'),
        ('Ethan Brown', 'V105', 'Bob'),
    ]

    # Candidate Table
    candidate_data = [
        ('Alice', 'Top leader with great experience.'),
        ('Bob', 'Experienced politician with strong credentials.'),
        ('Charlie', 'Young and dynamic leader.'),
    ]

    # Votes Table
    votes_data = [
        ('V101', 'Alice'),
        ('V102', 'Bob'),
        ('V103', 'Alice'),
        ('V104', 'Charlie'),
        ('V105', 'Alice'),
    ]

    # Insert data
    cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", user_data)
    cursor.executemany("INSERT INTO voters (name, voter_id, vote_casted) VALUES (?, ?, ?)", voter_data)
    cursor.executemany("INSERT INTO candidates (name, description) VALUES (?, ?)", candidate_data)
    cursor.executemany("INSERT INTO votes (voter_id, candidate) VALUES (?, ?)", votes_data)

    conn.commit()
    conn.close()

    print("[INFO] Database initialized successfully.")
    initialize_logs()


# =========================
# Log Initialization
# =========================
def initialize_logs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("[INFO] Database initialized successfully.\n")
            f.write("[INFO] Voter V101 cast a vote for Alice.\n")
            f.write("[INFO] Voter V102 cast a vote for Bob.\n")
            f.write("[INFO] System log initialized.\n")
        print("[INFO] system.log file created with mock data.")
    else:
        print("[INFO] system.log file already exists.")


# =========================
# Utility Functions
# =========================
def execute_query(query, params=None):
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        raise
    finally:
        conn.close()


def fetch_votes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT voter_id, candidate FROM votes")
        votes = cursor.fetchall()
        return votes
    finally:
        conn.close()


def write_log(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{message}\n")
    print(f"[LOG] {message}")
