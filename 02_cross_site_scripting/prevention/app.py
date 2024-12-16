from flask import Flask, render_template, request, redirect, url_for
from voting import voting_bp
from candidates import candidates_bp
from db import initialize_db
from xss_protection import detect_xss

app = Flask(__name__)
app.secret_key = 'secret_key'

# Register blueprints
app.register_blueprint(voting_bp)
app.register_blueprint(candidates_bp)

# Initialize database
initialize_db()

# Layer 1: Detect and block XSS payloads in requests
@app.before_request
def detect_xss_payloads():
    """
    Detect potential XSS payloads in form and query parameters.
    """
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

# Layer 4: Content Security Policy (CSP)
@app.after_request
def add_security_headers(response):
    """
    Add Content Security Policy (CSP) headers to the response.
    """
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
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
