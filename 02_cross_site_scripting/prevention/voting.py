from flask import Blueprint, render_template, request, redirect, url_for
from db import execute_query

voting_bp = Blueprint('voting', __name__, url_prefix='/voting')

@voting_bp.route('/')
def voting_page():
    # Layer 5: Output Escaping
    query = "SELECT name, description FROM candidates"
    candidates = execute_query(query)
    print("[INFO] Fetched candidates for the voting page.")
    return render_template('voting.html', candidates=candidates)

@voting_bp.route('/vote', methods=['POST'])
def vote_for_candidate():
    candidate = request.form['candidate']
    query = "INSERT INTO votes (candidate) VALUES (?)"
    execute_query(query, (candidate,))
    print(f"[INFO] Vote recorded for candidate: {candidate}")
    return redirect(url_for('voting_page'))
