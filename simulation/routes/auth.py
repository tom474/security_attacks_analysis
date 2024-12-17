from flask import Blueprint, render_template, request, redirect, url_for, session
from db import execute_query

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            query = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{password}'"
            print(f"[INFO] Executing query: {query}")
            results = execute_query(query)

            if results:
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
