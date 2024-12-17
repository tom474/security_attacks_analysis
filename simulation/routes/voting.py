from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import execute_query

voting_bp = Blueprint('voting', __name__, url_prefix='/voting')

@voting_bp.route('/')
def voting_page():
    query = "SELECT name, description FROM candidates"
    candidates = execute_query(query)
    print("[INFO] Fetched candidates for the voting page:")
    for candidate in candidates:
        print(f"    - Candidate: {candidate[0]}, Description: {candidate[1][:50]}{'...' if len(candidate[1]) > 50 else ''}")
    return render_template('voting.html', candidates=candidates)

@voting_bp.route('/vote', methods=['POST'])
def vote_for_candidate():
    name = request.form['name']
    voter_id = request.form['voter_id']
    candidate = request.form['candidate']

    try:
        print(f"[INFO] Processing vote for Voter ID: {voter_id}, Candidate: {candidate}")
        # Check if voter already exists in the table
        check_query = "SELECT * FROM voters WHERE voter_id = ?"
        existing_voter = execute_query(check_query, (voter_id,))

        if existing_voter:
            # Update the vote_casted for existing voter
            update_query = "UPDATE voters SET vote_casted = ? WHERE voter_id = ?"
            execute_query(update_query, (candidate, voter_id))
            print(f"[INFO] Updated vote for Voter ID: {voter_id}, Candidate: {candidate}")
            flash(f"Your vote has been updated to {candidate}.", "success")
        else:
            # Insert the voter and record the vote
            insert_query = "INSERT INTO voters (name, voter_id, vote_casted) VALUES (?, ?, ?)"
            execute_query(insert_query, (name, voter_id, candidate))
            print(f"[INFO] New vote recorded for Voter ID: {voter_id}, Name: {name}, Candidate: {candidate}")
            flash(f"Thank you, {name}! Your vote for {candidate} has been recorded.", "success")
    except Exception as e:
        print(f"[ERROR] Error recording vote: {e}")
        flash("An error occurred while recording your vote. Please try again.", "danger")

    return redirect(url_for('voting.voting_page'))
