import os
from flask import Flask, session, redirect, url_for, render_template
from datetime import timedelta
from zoneinfo import ZoneInfo
from auth import auth_bp
from routes.admin_routes import admin_bp
from routes.voter_routes import voter_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'ballotchain_secret_key_123'  # In production, use a proper secret key
app.permanent_session_lifetime = timedelta(minutes=30)

# Create required directories
os.makedirs('data', exist_ok=True)
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/receipts', exist_ok=True)
os.makedirs('static/images/candidates', exist_ok=True)

# Initialize JSON files if they don't exist
def init_json_file(filepath, default_data):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            import json
            json.dump(default_data, f)

init_json_file('data/blockchain.json', {"chain": [], "length": 0})
init_json_file('data/voters.json', {"voters": []})
init_json_file('data/candidates.json', {"candidates": []})
init_json_file('data/elections.json', {"current_election": None, "past_elections": []})

def initialize_data():
    if not os.path.exists('data'):
        os.makedirs('data')
        with open('data/blockchain.json', 'w') as f:
            json.dump({"chain": [], "length": 0}, f)
        # Add similar initialization for other files

# Call this function before registering blueprints
initialize_data()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(voter_bp, url_prefix='/voter')

@app.route('/')
def home():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('voter.dashboard'))
    return redirect(url_for('auth.login'))
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',
                         error_code="404",
                         error_name="Page Not Found",
                         error_description="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html',
                         error_code="500",
                         error_name="Internal Server Error",
                         error_description="Something went wrong on our end. Please try again later."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)