import re
import sqlite3
import os
import subprocess
import time
import psutil
from collections import defaultdict

# SQL Injection Detection Patterns
SQLI_PATTERNS = [
    r"(?i)union",           # UNION keyword
    r"(?i)select.*from",    # SELECT * FROM
    r"(?i)insert\s+into",   # INSERT INTO
    r"(?i)update.*set",     # UPDATE table SET
    r"(?i)delete\s+from",   # DELETE FROM
    r"(?i)drop\s+table",    # DROP TABLE
    r"--",                  # Comment marker
    r";",                   # Semicolon for chaining queries
]

# Allowed Queries for Whitelisting
ALLOWED_QUERIES = [
    "SELECT * FROM users WHERE username = ? AND password = ?",
    "SELECT * FROM voters WHERE voter_id = ?",
]

def log_attack(detection_layer, blocking_layer, query, reason):
    print(f"\n[SECURITY ALERT] SQL Injection detected!")
    print(f"  - Detected at: {detection_layer}")
    print(f"  - Blocked by: {blocking_layer}")
    print(f"  - Query: {query}")
    print(f"  - Reason: {reason}\n")

# Input Validation
def validate_input(input_data):
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, input_data):
            return False, f"Pattern matched: {pattern}"
    return True, None

# Input Normalization
def normalize_input(input_data):
    return input_data.strip().replace("\t", "").replace("\n", "")

# Query Whitelisting & Parameterized Query Execution
def execute_query(query, params=None):
    # Query Whitelisting
    if query not in ALLOWED_QUERIES:
        log_attack("Query Whitelisting", "Query Whitelisting", query, "Query not in allowed list.")
        raise Exception("Blocked due to query not in allowed list.")

    # Database connection
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    try:
        # Parameterized Query Execution
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


# XSS Detection
def detect_xss(input_string):
    patterns = [
        r"<script.*?>",  # Detect script tags
        r"on\w+="        # Detect inline event handlers (e.g., onclick, onmouseover)
    ]
    for pattern in patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

# Input Sanitization
def sanitize_input(input_string):
    sanitized = re.sub(r"[<>\"']", "", input_string)
    print(f"[INFO] Input sanitized: {sanitized}")
    return sanitized


# Filename Validation
def validate_filename(filename):
    if not re.match(r'^[a-zA-Z0-9_\-.]+$', filename):
        print("[WARNING] Invalid filename detected. Potential command injection attempt.")
        return False
    return True

# File Path Whitelisting
ALLOWED_REPORT_DIR = "reports"
ALLOWED_LOG_DIR = "logs"
ALLOWED_LOG_FILES = ["system.log"]

def is_allowed_report_path(filename):
    full_path = os.path.abspath(os.path.join(ALLOWED_REPORT_DIR, filename))
    if not full_path.startswith(os.path.abspath(ALLOWED_REPORT_DIR)):
        print(f"[WARNING] Report filename '{filename}' is outside the allowed directory. Blocked.")
        return False
    return True


def is_allowed_log_path(filename):
    # Ensure the filename is in the allowed list
    if filename not in ALLOWED_LOG_FILES:
        print(f"[WARNING] File '{filename}' is not in the allowed log files. Blocked.")
        return False

    # Ensure the full path is within the allowed directory
    full_path = os.path.abspath(os.path.join(ALLOWED_LOG_DIR, filename))
    if not full_path.startswith(os.path.abspath(ALLOWED_LOG_DIR)):
        print(f"[WARNING] Log file '{filename}' is outside the allowed directory. Blocked.")
        return False
    return True

# Secure Execution with Environment Isolation
def execute_secure_command(command, stdout=None, capture_output=True, env=None):
    try:
        result = subprocess.run(command, stdout=stdout, check=True, text=True, capture_output=capture_output, env=env)
        print(f"[INFO] Command executed successfully: {' '.join(command)}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command execution failed: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during command execution: {e}")
        raise
    

# Rate Limiting To Prevent Brute-force (in-memory for simplicity)
RATE_LIMIT = {"generate_report": {}, "view_logs": {}, "vote": {}}
RATE_LIMIT_WINDOW = 60       # 60 seconds
RATE_LIMIT_REQUESTS = 10     # Max 10 requests per window

def is_rate_limited(endpoint, client_ip):
    import time
    current_time = time.time()
    if endpoint not in RATE_LIMIT:
        RATE_LIMIT[endpoint] = {}
    if client_ip not in RATE_LIMIT[endpoint]:
        RATE_LIMIT[endpoint][client_ip] = []
    # Remove requests outside the time window
    RATE_LIMIT[endpoint][client_ip] = [t for t in RATE_LIMIT[endpoint][client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT[endpoint][client_ip]) >= RATE_LIMIT_REQUESTS:
        print(f"[WARNING] Rate limit exceeded for {client_ip} on endpoint {endpoint}.")
        return True
    # Add the current request
    RATE_LIMIT[endpoint][client_ip].append(current_time)
    return False