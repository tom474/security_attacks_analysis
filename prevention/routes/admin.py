from flask import Blueprint, render_template, request, redirect, url_for, session
# from db import execute_query, fetch_votes
from db import fetch_votes
from utils.security_utils import execute_query, validate_input, normalize_input, log_attack, detect_xss, sanitize_input, validate_filename, ALLOWED_REPORT_DIR, ALLOWED_LOG_DIR, is_allowed_report_path, is_allowed_log_path, execute_secure_command, is_rate_limited
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/search', methods=['GET', 'POST'])
def search_voter():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            voter_id = request.form['voter_id']

            # Input Validation
            valid_voter_id, reason = validate_input(voter_id)
            if not valid_voter_id:
                log_attack("Input Validation", "Input Validation", valid_voter_id, reason)
                return render_template('results.html', results=None, error="Invalid input detected.")
            
            # Input Normalization
            voter_id = normalize_input(voter_id)

            # Query Whitelisting & Parameterized Query Execution
            query = f"SELECT * FROM voters WHERE voter_id = ?"
            print(f"[INFO] Executing search query: {query}")
            results = execute_query(query, (voter_id,))
            return render_template('results.html', results=results)
        except Exception as e:
            print(f"[ERROR] Error during voter search: {e}")
            return render_template('results.html', error="An error occurred while fetching data.")
    return render_template('search.html')

@admin_bp.route('/add_candidate', methods=['GET', 'POST'])
def add_candidate():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        try:
            # XSS Detection - Input Validation
            if detect_xss(description):
                print("[WARNING] Potential XSS attack detected in candidate description.")
                print("[BLOCKED] Candidate addition blocked at input validation layer.")
                return redirect(url_for('admin.add_candidate'))
            
            # Input Sanitization
            sanitized_name = sanitize_input(name)
            sanitized_description = sanitize_input(description)

            query = "INSERT INTO candidates (name, description) VALUES (?, ?)"
            execute_query(query, (sanitized_name, sanitized_description))
            print(f"[INFO] Candidate '{name}' added successfully. Description: {description}")
            return redirect(url_for('voting.voting_page'))
        except Exception as e:
            print(f"[ERROR] Error adding candidate '{name}': {e}")
            return render_template('add_candidate.html', error="Failed to add candidate.")
    return render_template('add_candidate.html')

@admin_bp.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    # Rate Limiting
    client_ip = request.remote_addr
    if is_rate_limited("generate_report", client_ip):
        return render_template('generate_report.html', error="Rate limit exceeded. Try again later.")

    if request.method == 'POST':
        filename = request.form['filename']
        try:
            # Validate filename
            if not validate_filename(filename):
                return render_template('generate_report.html', error="Invalid filename. Operation blocked.")
            
            # Enforce allowed directory
            if not is_allowed_report_path(filename):
                return render_template('generate_report.html', error="Invalid report path. Operation blocked.")
            
            # Secure command execution
            report_content = str(fetch_votes())
            report_path = os.path.join(ALLOWED_REPORT_DIR, filename)
            print(f"[INFO] Writing report to '{report_path}' securely...")
            execute_secure_command(['echo', report_content], stdout=open(report_path, 'w'), capture_output=False)
            print("[INFO] Report generated successfully.")
            return render_template('report_result.html', filename=filename)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return render_template('report_result.html', error="Error generating the report.")
    return render_template('generate_report.html')

@admin_bp.route('/view_logs', methods=['GET', 'POST'])
def view_logs():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    # Rate Limiting
    client_ip = request.remote_addr
    if is_rate_limited("view_logs", client_ip):
        return render_template('view_logs.html', error="Rate limit exceeded. Try again later.")
    
    if request.method == 'POST':
        log_file = request.form['log_file']
        try:
            # Validate filename
            if not validate_filename(log_file):
                return render_template('view_logs.html', error="Invalid log file name. Operation blocked.")

            # Validate file path and whitelist
            if not is_allowed_log_path(log_file):
                return render_template('view_logs.html', error="Access to the specified file is not allowed. Operation blocked.")
            
            # Secure command execution
            log_path = os.path.join(ALLOWED_LOG_DIR, log_file)
            print(f"[INFO] Reading log file '{log_path}' securely...")
            log_content = execute_secure_command(['cat', log_path])
            print("[INFO] Log content fetched successfully.")
            return render_template('view_logs.html', log_content=log_content)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return render_template('view_logs.html', log_content="Error reading log file.")
    return render_template('view_logs.html', log_content=None)
