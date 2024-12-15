from flask import Flask, session, redirect, url_for
from auth import auth_bp
from voter import voter_bp
from db import initialize_db

app = Flask(__name__)
app.secret_key = 'secret_key'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(voter_bp)

# Initialize the database
initialize_db()

@app.route('/')
def home():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('voter.search_voter'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
