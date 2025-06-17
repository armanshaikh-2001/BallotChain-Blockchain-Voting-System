from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
from pathlib import Path

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

# Hardcoded admin credentials (in production, use proper authentication)
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "ballotchain123"
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        voter_id = request.form.get('voter_id')
        
        if username and password:  # Admin login
            if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
                session['role'] = 'admin'
                session['username'] = username
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid admin credentials', 'error')
        elif voter_id:  # Voter login
            voters = json.load(open('data/voters.json'))['voters']
            voter = next((v for v in voters if v['id'] == voter_id), None)
            
            if voter:
                if voter.get('has_voted', False):
                    flash('You have already voted!', 'error')
                else:
                    session['role'] = 'voter'
                    session['voter_id'] = voter_id
                    session['voter_name'] = voter.get('name', 'Voter')
                    return redirect(url_for('voter.dashboard'))
            else:
                flash('Invalid Voter ID', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))