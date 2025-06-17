from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from datetime import datetime
import pytz
import json
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from blockchain import Blockchain
from utils.pdf_gen import generate_results_pdf
from utils.qr_gen import generate_qr_code

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

@admin_bp.before_request
def require_admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
def dashboard():
    blockchain = Blockchain()
    voters = json.load(open('data/voters.json'))['voters']
    candidates = json.load(open('data/candidates.json'))['candidates']
    election = json.load(open('data/elections.json'))['current_election']
    
    total_voters = len(voters)
    voted = sum(1 for v in voters if v.get('has_voted', False))
    turnout = (voted / total_voters * 100) if total_voters > 0 else 0
    
    candidate_stats = []
    for candidate in candidates:
        votes = blockchain.get_votes_for_candidate(candidate['id'])
        if 'image' not in candidate:
            candidate['image'] = 'default_candidate.png'
        candidate_stats.append({
            'id': candidate['id'],
            'name': candidate['name'],
            'party': candidate.get('party', ''),
            'image': candidate.get('image', 'images/default_candidate.png'),  # ✅ add this line
            'votes': votes,
            'percentage': (votes / blockchain.get_total_votes() * 100) if blockchain.get_total_votes() > 0 else 0
        })

    
    # Sort candidates by votes
    candidate_stats.sort(key=lambda x: x['votes'], reverse=True)
    
    return render_template('admin/dashboard.html', 
                         election=election,
                         total_voters=total_voters,
                         voted=voted,
                         turnout=round(turnout, 2),
                         candidates=candidate_stats,
                         blockchain=blockchain)

@admin_bp.route('/add_candidate', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        manifesto = request.form.get('manifesto')
        image = request.files.get('image')
        
        if not name:
            flash('Name is required', 'error')
            return redirect(request.url)
        
        candidate_id = f"C{len(json.load(open('data/candidates.json'))['candidates']) + 1}"
        
        # Handle image upload
        image_path = "default_candidate.png"  # fallback

        if image and image.filename != '' and allowed_file(image.filename):
            filename = secure_filename(f"{candidate_id}_{image.filename}")
            image_path = f"images/candidates/{filename}"
            os.makedirs(os.path.join('static', 'images', 'candidates'), exist_ok=True)
            image.save(os.path.join('static', image_path))

        
        candidate = {
            'id': candidate_id,
            'name': name,
            'party': party,
            'manifesto': manifesto,
            'image': image_path
        }
        
        with open('data/candidates.json', 'r+') as f:
            data = json.load(f)
            data['candidates'].append(candidate)
            f.seek(0)
            json.dump(data, f, indent=4)
        
        flash('Candidate added successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/add_candidate.html')

@admin_bp.route('/modify_candidate/<candidate_id>', methods=['GET', 'POST'])
def modify_candidate(candidate_id):
    candidates = load_data('data/candidates.json')['candidates']
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)

    if request.method == 'POST':
        candidate['name'] = request.form['name']
        candidate['party'] = request.form['party']
        candidate['motto'] = request.form['motto']
        
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join('static/images/candidates', filename))
                candidate['image'] = f"images/candidates/{filename}"


        save_data('data/candidates.json', {'candidates': candidates})
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/modify_candidate.html', candidate=candidate)


@admin_bp.route('/delete_candidate/<candidate_id>')
def delete_candidate(candidate_id):
    with open('data/candidates.json', 'r+') as f:
        data = json.load(f)
        data['candidates'] = [c for c in data['candidates'] if c['id'] != candidate_id]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    
    flash('Candidate deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/manage_voters', methods=['GET', 'POST'])
def manage_voters():
    if request.method == 'POST':
        if 'voter_file' in request.files:
            file = request.files['voter_file']
            if file.filename.endswith('.json'):
                try:
                    new_voters = json.load(file)['voters']
                except:
                    flash('Invalid JSON file format', 'error')
                    return redirect(request.url)
            elif file.filename.endswith('.csv'):
                import csv
                new_voters = []
                try:
                    csv_reader = csv.DictReader(file.read().decode('utf-8').splitlines())
                    for row in csv_reader:
                        new_voters.append({'id': row['id'], 'name': row.get('name', 'Voter')})
                except:
                    flash('Invalid CSV file format', 'error')
                    return redirect(request.url)
            else:
                flash('Unsupported file type', 'error')
                return redirect(request.url)
            
            with open('data/voters.json', 'r+') as f:
                data = json.load(f)
                existing_ids = {v['id'] for v in data['voters']}
                
                added = 0
                for voter in new_voters:
                    if voter['id'] not in existing_ids:
                        voter['has_voted'] = False
                        data['voters'].append(voter)
                        added += 1
                
                f.seek(0)
                json.dump(data, f, indent=4)
            
            flash(f'Added {added} new voters', 'success')
            return redirect(url_for('admin.manage_voters'))
        else:
            # Manual voter addition
            voter_id = request.form.get('voter_id')
            voter_name = request.form.get('voter_name')
            
            if not voter_id:
                flash('Voter ID is required', 'error')
                return redirect(request.url)
            
            with open('data/voters.json', 'r+') as f:
                data = json.load(f)
                if any(v['id'] == voter_id for v in data['voters']):
                    flash('Voter ID already exists', 'error')
                    return redirect(request.url)
                
                data['voters'].append({
                    'id': voter_id,
                    'name': voter_name or 'Voter',
                    'has_voted': False
                })
                f.seek(0)
                json.dump(data, f, indent=4)
            
            flash('Voter added successfully', 'success')
            return redirect(url_for('admin.manage_voters'))
    
    voters = json.load(open('data/voters.json'))['voters']
    return render_template('admin/manage_voters.html', voters=voters)

@admin_bp.route('/delete_voter/<voter_id>')
def delete_voter(voter_id):
    with open('data/voters.json', 'r+') as f:
        data = json.load(f)
        data['voters'] = [v for v in data['voters'] if v['id'] != voter_id]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    
    flash('Voter deleted successfully', 'success')
    return redirect(url_for('admin.manage_voters'))

@admin_bp.route('/election_control', methods=['POST'])
def election_control():
    action = request.form.get('action')
    elections = {}
    
    try:
        with open('data/elections.json', 'r') as f:
            elections = json.load(f)
    except:
        elections = {"current_election": None, "past_elections": []}
    
    if action == 'start':
        election_name = request.form.get('election_name')
        end_time = request.form.get('end_time')
        
        if not election_name:
            flash('Election name is required', 'error')
            return redirect(url_for('admin.dashboard'))
        
        ist = pytz.timezonw('Asia/Kolkata')
        start_time = datetime.now(ist)
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M').replace(tzinfo=ist)
    
        elections['current_election'] = {
            'name': election_name,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': 'active'
        }
        
        flash('Election started successfully', 'success')
    elif action == 'end':
        if elections['current_election']:
            elections['past_elections'].append(elections['current_election'])
            elections['current_election'] = None
            flash('Election ended successfully', 'success')
        else:
            flash('No active election to end', 'error')
    elif action == 'pause':
        if elections['current_election']:
            elections['current_election']['status'] = 'paused'
            flash('Election paused', 'success')
        else:
            flash('No active election to pause', 'error')
    elif action == 'resume':
        if elections['current_election']:
            elections['current_election']['status'] = 'active'
            flash('Election resumed', 'success')
        else:
            flash('No active election to resume', 'error')
    
    with open('data/elections.json', 'w') as f:
        json.dump(elections, f, indent=4)
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_blockchain')
def view_blockchain():
    blockchain = Blockchain()
    return render_template('admin/view_blockchain.html', blockchain=blockchain.chain)

@admin_bp.route('/export_blockchain')
def export_blockchain():
    return send_file('data/blockchain.json', as_attachment=True)

@admin_bp.route('/export_results_pdf')
def export_results_pdf():
    blockchain = Blockchain()
    voters = json.load(open('data/voters.json'))['voters']
    candidates = json.load(open('data/candidates.json'))['candidates']
    election = json.load(open('data/elections.json'))['current_election']
    
    total_voters = len(voters)
    voted = sum(1 for v in voters if v.get('has_voted', False))
    turnout = (voted / total_voters * 100) if total_voters > 0 else 0
    
    candidate_stats = []
    for candidate in candidates:
        votes = blockchain.get_votes_for_candidate(candidate['id'])
        candidate_stats.append({
            'id': candidate['id'],
            'name': candidate['name'],
            'party': candidate.get('party', ''),
            'votes': votes,
            'percentage': (votes / blockchain.get_total_votes() * 100) if blockchain.get_total_votes() > 0 else 0
        })
    
    candidate_stats.sort(key=lambda x: x['votes'], reverse=True)
    
    pdf_path = generate_results_pdf(election, candidate_stats, total_voters, voted, turnout)
    return send_file(pdf_path, as_attachment=True)

@admin_bp.route('/verify_blockchain')
def verify_blockchain():
    blockchain = Blockchain()
    is_valid = blockchain.is_chain_valid()
    
    if is_valid:
        flash('Blockchain is valid - no tampering detected', 'success')
    else:
        flash('WARNING: Blockchain has been tampered with!', 'error')
    
    return redirect(url_for('admin.view_blockchain'))