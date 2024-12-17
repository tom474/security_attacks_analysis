from flask import Flask, session, redirect, url_for, render_template
from routes.auth import auth_bp
from routes.voting import voting_bp
from routes.admin import admin_bp
from db import initialize_db

app = Flask(__name__)
app.secret_key = 'secret_key'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(voting_bp)
app.register_blueprint(admin_bp)

# Initialize the database
initialize_db()

@app.route('/')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    return render_template('home.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
