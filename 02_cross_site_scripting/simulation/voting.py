from flask import Blueprint, render_template, request, redirect, url_for
from db import execute_query

voting_bp = Blueprint('voting', __name__, url_prefix='/voting')

@voting_bp.route('/')
def voting_page():
    # Fetch all candidates and their descriptions
    query = "SELECT name, description FROM candidates"
    candidates = execute_query(query)
    print("[INFO] Fetched candidates for the voting page:")
    for candidate in candidates:
        print(f"    - Candidate: {candidate[0]}, Description: {candidate[1][:50]}{'...' if len(candidate[1]) > 50 else ''}")
    return render_template('voting.html', candidates=candidates)

@voting_bp.route('/vote', methods=['POST'])
def vote_for_candidate():
    candidate = request.form['candidate']
    query = "INSERT INTO votes (candidate) VALUES (?)"
    execute_query(query, (candidate,))
    print(f"[INFO] Vote recorded for candidate: {candidate}")
    return redirect(url_for('voting_page'))
