import os
import re
import subprocess
from flask import Blueprint, render_template, request
from db import fetch_votes

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Layer 1: Input Validation
def validate_filename(filename):
    """
    Validate filename to allow only alphanumeric characters, underscores, and dots.
    """
    if not re.match(r'^[a-zA-Z0-9_\-.]+$', filename):
        print("[WARNING] Invalid filename detected. Potential command injection attempt.")
        return False
    return True

# Layer 2: File Path Whitelisting
ALLOWED_REPORT_DIR = "reports"
ALLOWED_LOG_DIR = "logs"
ALLOWED_LOG_FILES = ["system.log"]

def is_allowed_report_path(filename):
    """
    Ensure the report filename is within the allowed directory.
    """
    full_path = os.path.abspath(os.path.join(ALLOWED_REPORT_DIR, filename))
    if not full_path.startswith(os.path.abspath(ALLOWED_REPORT_DIR)):
        print(f"[WARNING] Report filename '{filename}' is outside the allowed directory. Blocked.")
        return False
    return True


def is_allowed_log_path(filename):
    """
    Validate and ensure the log file is within the allowed directory and whitelisted.
    """
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


# Layer 3: Secure Execution with Environment Isolation
def execute_secure_command(command, env=None):
    """
    Execute commands securely using subprocess.run() in a restricted environment.
    """
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, env=env)
        print(f"[INFO] Command executed successfully: {' '.join(command)}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command execution failed: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error during command execution: {e}")
        raise

# Layer 4: Rate Limiting (in-memory for simplicity)
RATE_LIMIT = {"generate_report": {}, "view_logs": {}}
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_REQUESTS = 5  # Max 5 requests per window


def is_rate_limited(endpoint, client_ip):
    """
    Simple in-memory rate limiting for endpoints.
    """
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

@admin_bp.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    """
    Secure report generation with multiple security layers, using subprocess for execution.
    """
    client_ip = request.remote_addr
    if is_rate_limited("generate_report", client_ip):
        return "<h3>Rate limit exceeded. Try again later.</h3>"

    if request.method == 'POST':
        filename = request.form['filename']

        # Layer 1: Validate filename
        if not validate_filename(filename):
            return "<h3>Invalid filename. Operation blocked.</h3>"

        # Layer 2: Enforce allowed directory
        if not is_allowed_report_path(filename):
            return "<h3>Invalid report path. Operation blocked.</h3>"

        # Layer 3: Generate the report using subprocess
        report_content = str(fetch_votes())
        report_path = os.path.join(ALLOWED_REPORT_DIR, filename)

        try:
            print(f"[INFO] Writing report to '{report_path}' securely...")
            # Use subprocess to echo content into the file
            subprocess.run(['echo', report_content], stdout=open(report_path, 'w'), check=True)
            print("[INFO] Report generated successfully.")
            return render_template('report_result.html', filename=report_path)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Subprocess command failed: {e}")
            return "<h3>Error generating the report. Check server logs.</h3>"
        except Exception as e:
            print(f"[ERROR] Unexpected error during report generation: {e}")
            return "<h3>Error generating the report. Check server logs.</h3>"

    return render_template('generate_report.html')


@admin_bp.route('/view_logs', methods=['GET', 'POST'])
def view_logs():
    """
    Secure log viewing with directory and file whitelisting, using subprocess for execution.
    """
    client_ip = request.remote_addr
    if is_rate_limited("view_logs", client_ip):
        return "<h3>Rate limit exceeded. Try again later.</h3>"

    if request.method == 'POST':
        log_file = request.form['log_file']

        # Layer 1: Validate filename
        if not validate_filename(log_file):
            return "<h3>Invalid log file name. Operation blocked.</h3>"

        # Layer 2: Validate file path and whitelist
        if not is_allowed_log_path(log_file):
            return "<h3>Access to the specified file is not allowed. Operation blocked.</h3>"

        try:
            # Layer 3: Use subprocess to read the log file securely
            full_path = os.path.join(ALLOWED_LOG_DIR, log_file)
            print(f"[INFO] Reading log file '{full_path}' securely...")
            result = subprocess.run(['cat', full_path], check=True, text=True, capture_output=True)
            log_content = result.stdout
            print("[INFO] Log content fetched successfully.")
            return render_template('view_logs.html', log_content=log_content)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Subprocess command failed: {e}")
            return "<h3>Error fetching the log file. Check server logs.</h3>"
        except FileNotFoundError:
            print("[WARNING] Log file not found.")
            return "<h3>Log file not found.</h3>"
        except Exception as e:
            print(f"[ERROR] Unexpected error during log reading: {e}")
            return "<h3>Error fetching the log file. Check server logs.</h3>"

    return render_template('view_logs.html', log_content=None)
