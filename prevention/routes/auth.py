from flask import Blueprint, render_template, request, redirect, url_for, session
# from db import execute_query
from utils.security_utils import execute_query, validate_input, normalize_input, log_attack

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Input Validation
            valid_username, reason = validate_input(username)
            valid_password, reason2 = validate_input(password)

            if not valid_username or not valid_password:
                log_attack("Input Validation", "Input Validation", f"Username: {username}, Password: {password}", reason or reason2)
                return render_template('login.html', error="Invalid input detected.")

            # Input Normalization
            username = normalize_input(username)
            password = normalize_input(password)

            # Query Whitelisting & Parameterized Query Execution
            query = f"SELECT * FROM users WHERE username = ? AND password = ?"
            print(f"[INFO] Executing query: {query}")
            results = execute_query(query, (username, password))

            if results:
                # Session management
                session['logged_in'] = True
                session['username'] = username
                print(f"[INFO] Successful login for user: {username}")
                return redirect(url_for('home'))
            else:
                print(f"[WARNING] Login failed for user: '{username}'")
                return render_template('login.html', error="Invalid credentials")
        except Exception as e:
            print(f"[ERROR] An error occurred during login: {e}")
            return render_template('login.html', error="An unexpected error occurred.")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
