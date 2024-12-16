import os
from flask import Blueprint, render_template, request
from db import fetch_votes

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    """
    Report generation with a simulated command injection vulnerability.
    """
    if request.method == 'POST':
        filename = request.form['filename']

        # Vulnerable command
        command = f"echo '{fetch_votes()}' > {filename}"
        print(f"[DEBUG] Executing command: {command}")
        try:
            os.system(command)  # Simulated vulnerable system call
            return render_template('report_result.html', filename=filename)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return "<h3>Error generating the report. Check the server logs.</h3>"

    return render_template('generate_report.html')

@admin_bp.route('/view_logs', methods=['GET', 'POST'])
def view_logs():
    """
    Log viewing with simulated command injection vulnerability.
    """
    if request.method == 'POST':
        log_file = request.form['log_file']

        # Vulnerable command
        command = f"cat {log_file}"
        print(f"[DEBUG] Executing command: {command}")
        try:
            log_content = os.popen(command).read()
            return render_template('view_logs.html', log_content=log_content)
        except Exception as e:
            print(f"[ERROR] Command execution failed: {e}")
            return "<h3>Error viewing the log file. Check the server logs.</h3>"

    return render_template('view_logs.html', log_content=None)
