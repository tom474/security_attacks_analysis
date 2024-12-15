import sqlite3

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

def execute_query(query):
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except sqlite3.Error as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()
