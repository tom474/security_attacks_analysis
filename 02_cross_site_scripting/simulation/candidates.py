from flask import Blueprint, render_template, request, redirect, url_for
from db import execute_query

candidates_bp = Blueprint('candidates', __name__, url_prefix='/candidates')

@candidates_bp.route('/add', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Add the candidate to the database
        query = "INSERT INTO candidates (name, description) VALUES (?, ?)"
        execute_query(query, (name, description))
        print(f"[INFO] Candidate added: {name}")
        print(f"[INFO] Description: {description[:50]}{'...' if len(description) > 50 else ''}")
        return redirect(url_for('voting.voting_page'))

    return render_template('add_candidate.html')
