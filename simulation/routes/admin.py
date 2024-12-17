from flask import Blueprint, render_template, request, redirect, url_for, session
from db import execute_query, fetch_votes
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/search', methods=['GET', 'POST'])
def search_voter():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        try:
            query = f"SELECT * FROM voters WHERE voter_id = '{voter_id}'"
            if ";" in query:
                commands = query.split(";")
                results = []
                for command in commands:
                    command = command.strip()
                    print(f"[INFO] Executing query: {command}")
                    results.append(execute_query(command))
                return render_template('results.html', commands=commands, results=results)
            print(f"[INFO] Executing query: {query}")
            results = execute_query(query)
            return render_template('results.html', results=results)
        except Exception as e:
            print(f"[ERROR] Error during voter search: {e}")
            return render_template('results.html', error="An error occurred while fetching data.")
    return render_template('search.html')

@admin_bp.route('/add_candidate', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        try:
            query = "INSERT INTO candidates (name, description) VALUES (?, ?)"
            execute_query(query, (name, description))
            print(f"[INFO] Candidate '{name}' added successfully. Description: {description}")
            return redirect(url_for('voting.voting_page'))
        except Exception as e:
            print(f"[ERROR] Error adding candidate '{name}': {e}")
            return render_template('add_candidate.html', error="Failed to add candidate.")
    return render_template('add_candidate.html')

@admin_bp.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'POST':
        filename = request.form['filename']
        filepath = "reports/" + filename
        try:
            command = f"echo '{fetch_votes()}' > {filepath}"
            print(f"[DEBUG] Executing command: {command}")
            os.system(command)
            return render_template('report_result.html', filename=filename)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return render_template('report_result.html', error="Error generating the report.")
    return render_template('generate_report.html')

@admin_bp.route('/view_logs', methods=['GET', 'POST'])
def view_logs():
    if request.method == 'POST':
        log_file = request.form['log_file']
        log_path = "logs/" + log_file
        try:
            command = f"cat {log_path}"
            print(f"[DEBUG] Executing command: {command}")
            log_content = os.popen(command).read()
            return render_template('view_logs.html', log_content=log_content)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return render_template('view_logs.html', log_content="Error reading log file.")
    return render_template('view_logs.html', log_content=None)
