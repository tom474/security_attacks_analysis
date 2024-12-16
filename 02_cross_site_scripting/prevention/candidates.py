from flask import Blueprint, render_template, request, redirect, url_for
from db import execute_query
from xss_protection import sanitize_input, detect_xss

candidates_bp = Blueprint('candidates', __name__, url_prefix='/candidates')

@candidates_bp.route('/add', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Layer 2: XSS Detection - Input Validation
        if detect_xss(description):
            print("[WARNING] Potential XSS attack detected in candidate description.")
            print("[BLOCKED] Candidate addition blocked at input validation layer.")
            return redirect(url_for('candidates.add_candidate'))

        # Layer 3: Input Sanitization
        sanitized_name = sanitize_input(name)
        sanitized_description = sanitize_input(description)

        # Add the candidate to the database
        query = "INSERT INTO candidates (name, description) VALUES (?, ?)"
        execute_query(query, (sanitized_name, sanitized_description))
        print("[INFO] Candidate added successfully after sanitization.")
        return redirect(url_for('voting.voting_page'))

    return render_template('add_candidate.html')
