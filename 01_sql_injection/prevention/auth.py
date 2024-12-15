from flask import Blueprint, render_template, request, redirect, url_for, session
from db import execute_query, validate_input, normalize_input, log_attack

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Layer 1: Input Validation
        valid_username, reason = validate_input(username)
        valid_password, reason2 = validate_input(password)

        if not valid_username or not valid_password:
            log_attack("Input Validation", "Input Validation", f"Username: {username}, Password: {password}", reason or reason2)
            return render_template('login.html', error="Invalid input detected.")

        # Layer 2: Input Normalization
        username = normalize_input(username)
        password = normalize_input(password)

        # Layer 3, 4: Query Whitelisting & Parameterized Query Execution
        query = "SELECT * FROM admins WHERE username = ? AND password = ?"
        print(f"[INFO] Executing login query: {query}")
        results = execute_query(query, (username, password))

        if results:
            session['logged_in'] = True
            session['username'] = username
            print(f"[INFO] Successful login for user: {username}")
            return redirect(url_for('voter.search_voter'))
        else:
            print(f"[WARNING] Failed login attempt for user: {username}")
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
