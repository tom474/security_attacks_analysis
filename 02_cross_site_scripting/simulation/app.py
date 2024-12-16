from flask import Flask, render_template
from voting import voting_bp
from candidates import candidates_bp
from db import initialize_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register blueprints
app.register_blueprint(voting_bp)
app.register_blueprint(candidates_bp)

# Initialize database
initialize_db()

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
