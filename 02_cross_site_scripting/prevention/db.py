import sqlite3

def initialize_db():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    # Drop and recreate tables
    cursor.execute("DROP TABLE IF EXISTS candidates")
    cursor.execute("DROP TABLE IF EXISTS votes")

    cursor.execute('''
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL
        )
    ''')

    # Insert mock candidates with Scenario 3 script
    print("[INFO] Initializing database with candidates...")
    cursor.execute("INSERT INTO candidates (name, description) VALUES ('Alice', 'Top leader')")
    cursor.execute("INSERT INTO candidates (name, description) VALUES ('Bob', 'Experienced politician')")
    print("[INFO] Database initialized with candidates: Alice, Bob, and Tom (with malicious script).")
    conn.commit()
    conn.close()


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
