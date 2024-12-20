from flask import Blueprint, render_template, request, redirect, url_for, session, flash
# from db import execute_query
from utils.security_utils import execute_query, validate_input, is_rate_limited

voting_bp = Blueprint('voting', __name__, url_prefix='/voting')

# Variables for IP Blocking
BLOCKED_IPS = set()
IP_THRESHOLD = 10     # Max allowed failures before blocking
FAILED_REQUESTS = {}  # Tracks failed requests per IP

# Track failed requests and block IP if necessary
def track_failed_request(client_ip):
    global FAILED_REQUESTS, BLOCKED_IPS
    if client_ip not in FAILED_REQUESTS:
        FAILED_REQUESTS[client_ip] = 0
    FAILED_REQUESTS[client_ip] += 1

    if FAILED_REQUESTS[client_ip] >= IP_THRESHOLD:
        BLOCKED_IPS.add(client_ip)
        print(f"[WARNING] IP {client_ip} has been blocked due to excessive failed requests.")


@voting_bp.route('/')
def voting_page():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    # Output Escaping
    query = "SELECT name, description FROM candidates"
    candidates = execute_query(query)
    print("[INFO] Fetched candidates for the voting page:")
    for candidate in candidates:
        print(f"    - Candidate: {candidate[0]}, Description: {candidate[1][:50]}{'...' if len(candidate[1]) > 50 else ''}")
    return render_template('voting.html', candidates=candidates)

@voting_bp.route('/vote', methods=['POST'])
def vote_for_candidate():
    client_ip = request.remote_addr

    # IP Blocking
    if client_ip in BLOCKED_IPS:
        print(f"[BLOCKED] IP {client_ip} attempted to access '/vote'.")
        return "Your IP has been blocked due to suspicious activity.", 403

    # Rate Limiting
    if is_rate_limited("vote", client_ip):
        track_failed_request(client_ip)
        return "Too many requests. Please try again later.", 429

    name = request.form['name']
    voter_id = request.form['voter_id']
    candidate = request.form['candidate']

    try:
        # Input Validation
        valid_voter_id, reason = validate_input(voter_id)
        valid_candidate, reason2 = validate_input(candidate)

        if not valid_voter_id or not valid_candidate:
            print(f"[WARNING] Invalid input detected from IP {client_ip}: {reason or reason2}")
            flash("Invalid input detected. Please try again.", "danger")
            track_failed_request(client_ip)
            return redirect(url_for('voting.voting_page'))

        # Check if voter exists
        check_query = "SELECT * FROM voters WHERE voter_id = ?"
        existing_voter = execute_query(check_query, (voter_id,))

        if existing_voter:
            # Update vote for existing voter
            update_query = "UPDATE voters SET vote_casted = ? WHERE voter_id = ?"
            execute_query(update_query, (candidate, voter_id))
            print(f"[INFO] Updated vote for Voter ID: {voter_id}, Candidate: {candidate}")
            flash(f"Your vote has been updated to {candidate}.", "success")
        else:
            # Insert new voter and vote
            insert_query = "INSERT INTO voters (name, voter_id, vote_casted) VALUES (?, ?, ?)"
            execute_query(insert_query, (name, voter_id, candidate))
            print(f"[INFO] New vote recorded for Voter ID: {voter_id}, Name: {name}, Candidate: {candidate}")
            flash(f"Thank you, {name}! Your vote for {candidate} has been recorded.", "success")
    except Exception as e:
        print(f"[ERROR] Error recording vote: {e}")
        track_failed_request(client_ip)
        flash("An error occurred while recording your vote. Please try again.", "danger")

    return redirect(url_for('voting.voting_page'))
