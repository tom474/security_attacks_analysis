from flask import Blueprint, render_template, request, session, redirect, url_for
from db import execute_query

voter_bp = Blueprint('voter', __name__, url_prefix='/voter')

@voter_bp.route('/search', methods=['GET', 'POST'])
def search_voter():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        voter_id = request.form['voter_id']
        try:
            # Normal query processing
            query = f"SELECT * FROM voters WHERE voter_id = '{voter_id}'"
            if ";" in query:
                commands = query.split(";")
                results = []
                for command in commands:
                    command = command.strip()
                    print(f"[INFO] Executing search query: {command}")
                    results.append(execute_query(command))
                return render_template('results.html', commands=commands, results=results)
            print(f"[INFO] Executing search query: {query}")
            results = execute_query(query)
            return render_template('results.html', results=results)

        except Exception as e:
            # Log the error in the console but hide it from the user
            print(f"[ERROR] An error occurred during search: {e}")
            return render_template('results.html', results=None, error="An unexpected error occurred.")
    return render_template('search.html')
