from flask import Flask, session, redirect, url_for, render_template, request
from routes.auth import auth_bp
from routes.voting import voting_bp
from routes.admin import admin_bp
from db import initialize_db
from utils.security_utils import detect_xss

app = Flask(__name__)
app.secret_key = 'secret_key'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(voting_bp)
app.register_blueprint(admin_bp)

# Initialize the database
initialize_db()

# Block Malicious IPs
BLOCKED_IPS = ["192.168.1.100", "203.0.113.15"]
@app.before_request
def block_malicious_ips():
    if request.remote_addr in BLOCKED_IPS:
        print("[WARNING] Malicious IP detected. Blocking request.")
        return redirect(url_for('auth.login'))
    
    
# Detect and block XSS payloads in requests
@app.before_request
def detect_xss_payloads():
    for key, value in request.form.items():
        if detect_xss(value):
            print("[WARNING] XSS attack detected in form input.")
            print(f"[BLOCKED] Input '{key}' blocked at middleware layer.")
            return redirect(url_for('home'))

    for key, value in request.args.items():
        if detect_xss(value):
            print("[WARNING] XSS attack detected in query parameter.")
            print(f"[BLOCKED] Query parameter '{key}' blocked at middleware layer.")
            return redirect(url_for('home'))
        
# Content Security Policy (CSP)
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self'; "
    )
    print("[INFO] Content Security Policy (CSP) applied.")
    return response

@app.route('/')
def home():
    # Authentication
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    return render_template('home.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
