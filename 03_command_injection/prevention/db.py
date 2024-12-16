import sqlite3
import os

def initialize_logs():
    logs_dir = "logs"
    reports_dir = "reports"
    log_file = os.path.join(logs_dir, "system.log")

    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("[INFO] Database connection established.\n")
            f.write("[INFO] Voter V101 cast a vote for Alice.\n")
            f.write("[INFO] Voter V102 cast a vote for Bob.\n")
            f.write("[WARNING] Suspicious activity detected from IP 192.168.1.101.\n")
            f.write("[ERROR] Failed login attempt for admin at 2024-12-14 10:15:30\n")
        print("[INFO] system.log file created with mock data.")
    else:
        print("[INFO] system.log file already exists.")

def initialize_db():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    # Drop and recreate tables
    cursor.execute("DROP TABLE IF EXISTS votes")
    cursor.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT NOT NULL,
            candidate TEXT NOT NULL
        )
    ''')

    # Insert mock votes
    cursor.executemany(
        "INSERT INTO votes (voter_id, candidate) VALUES (?, ?)",
        [
            ('V101', 'Alice'),
            ('V102', 'Bob'),
            ('V103', 'Alice'),
            ('V104', 'Charlie'),
            ('V105', 'Alice'),
        ]
    )
    conn.commit()
    print("[INFO] Database initialized with mock votes.")
    conn.close()

    initialize_logs()


def fetch_votes():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM votes")
    votes = cursor.fetchall()
    conn.close()
    return votes
