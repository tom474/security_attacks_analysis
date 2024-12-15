from flask import Blueprint, render_template, request, session, redirect, url_for
from db import execute_query, validate_input, normalize_input, log_attack

voter_bp = Blueprint('voter', __name__, url_prefix='/voter')

@voter_bp.route('/search', methods=['GET', 'POST'])
def search_voter():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        voter_id = request.form['voter_id']

        # Layer 1: Input Validation
        valid, reason = validate_input(voter_id)
        if not valid:
            log_attack("Input Validation", "Input Validation", voter_id, reason)
            return render_template('results.html', results=None, error="Invalid input detected.")

        # Layer 2: Input Normalization
        voter_id = normalize_input(voter_id)

        # Layer 3, 4: Query Whitelisting & Parameterized Query Execution
        query = "SELECT * FROM voters WHERE voter_id = ?"
        print(f"[INFO] Executing search query: {query}")
        results = execute_query(query, (voter_id,))
        return render_template('results.html', results=results)

    return render_template('search.html')
