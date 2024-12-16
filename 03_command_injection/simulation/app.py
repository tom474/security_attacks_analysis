from flask import Flask, render_template
from admin import admin_bp
from db import initialize_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register blueprints
app.register_blueprint(admin_bp)

# Initialize the database
initialize_db()

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
