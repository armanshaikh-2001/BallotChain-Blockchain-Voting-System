from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
from datetime import datetime
import dateutil.parser
from blockchain import Blockchain
from utils.pdf_gen import generate_voter_receipt
from utils.qr_gen import generate_qr_code
import hashlib
import pytz  # Added for timezone support

voter_bp = Blueprint('voter', __name__, template_folder='templates/voter')

@voter_bp.before_request
def require_voter():
    if 'role' not in session or session['role'] != 'voter':
        return redirect(url_for('auth.login'))

@voter_bp.route('/')
def dashboard():
    try:
        with open('data/elections.json', 'r') as f:
            election = json.load(f).get('current_election')
    except:
        election = None
        
    if not election or election.get('status') != 'active':
        return render_template('voter/dashboard.html', election=None)
    
    return render_template('voter/dashboard.html', election=election)

@voter_bp.route('/candidates')
def candidates():
    try:
        with open('data/elections.json', 'r') as f:
            election = json.load(f).get('current_election')
    except:
        election = None
    
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Parse end time with timezone support
    end_time = None
    if election and 'end_time' in election:
        try:
            end_time = dateutil.parser.parse(election['end_time'])
            if not end_time.tzinfo:  # If no timezone info, assume IST
                end_time = ist.localize(end_time)
        except:
            end_time = None
    
    # Check if election is active and not expired
    is_active = (election and 
                election.get('status') == 'active' and 
                (end_time is None or now < end_time))
    
    candidates = []
    try:
        with open('data/candidates.json', 'r') as f:
            candidates = json.load(f).get('candidates', [])
    except:
        pass
    
    return render_template('voter/candidates.html', 
                         candidates=candidates,
                         election=election,
                         is_active=is_active,
                         now=now,
                         end_time=end_time)

@voter_bp.route('/cast_vote', methods=['POST'])
def cast_vote():
    try:
        with open('data/elections.json', 'r') as f:
            election = json.load(f).get('current_election')
    except:
        election = None

    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Parse end time with timezone support
    end_time = None
    if election and 'end_time' in election:
        try:
            end_time = dateutil.parser.parse(election['end_time'])
            if not end_time.tzinfo:  # If no timezone info, assume IST
                end_time = ist.localize(end_time)
        except:
            end_time = None

    if not (election and 
            election.get('status') == 'active' and 
            (end_time is None or now < end_time)):
        flash('Voting is currently closed', 'error')
        return redirect(url_for('voter.dashboard'))

    candidate_id = request.form.get('candidate_id')
    if not candidate_id:
        flash('No candidate selected', 'error')
        return redirect(url_for('voter.candidates'))

    # Check if candidate exists
    try:
        with open('data/candidates.json', 'r') as f:
            candidates = json.load(f).get('candidates', [])
    except:
        candidates = []
    
    if not any(c['id'] == candidate_id for c in candidates):
        flash('Invalid candidate selected', 'error')
        return redirect(url_for('voter.candidates'))

    # Check if already voted
    voter_id = session['voter_id']
    try:
        with open('data/voters.json', 'r') as f:
            voters = json.load(f).get('voters', [])
    except:
        voters = []
    
    voter = next((v for v in voters if v['id'] == voter_id), None)

    if not voter:
        flash('Voter not found', 'error')
        return redirect(url_for('auth.logout'))

    if voter.get('has_voted', False):
        flash('You have already voted!', 'error')
        return redirect(url_for('voter.dashboard'))

    # Create hashed voter token
    salt = "ballotchain_salt_123"  # In production, use a secure random salt
    voter_token = hashlib.sha256(f"{voter_id}{salt}".encode()).hexdigest()

    # Add vote to blockchain
    blockchain = Blockchain()
    block = blockchain.add_vote(voter_token, candidate_id)

    # Mark voter as voted
    try:
        with open('data/voters.json', 'r+') as f:
            data = json.load(f)
            for v in data['voters']:
                if v['id'] == voter_id:
                    v['has_voted'] = True
                    break
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    except Exception as e:
        flash('Error updating voter record', 'error')
        return redirect(url_for('voter.dashboard'))

    # Generate QR code
    qr_data = {
        'voter_token': voter_token,
        'candidate_id': candidate_id,
        'block_hash': block['hash'],
        'timestamp': block['timestamp']
    }

    qr_filename = f"static/qrcodes/{voter_token}.png"
    generate_qr_code(str(qr_data), qr_filename)

    # Generate receipt
    candidate = next(c for c in candidates if c['id'] == candidate_id)
    receipt_data = {
        'voter_id': voter_id,
        'voter_name': session.get('voter_name', 'Voter'),
        'candidate_name': candidate['name'],
        'candidate_party': candidate.get('party', ''),
        'timestamp': block['timestamp'],
        'block_hash': block['hash'],
        'qr_code': qr_filename
    }

    receipt_path = generate_voter_receipt(receipt_data)

    # Store session data for receipt view
    session['receipt_data'] = {
        'voter_id': voter_id,
        'candidate_name': candidate['name'],
        'timestamp': block['timestamp'],
        'block_hash': block['hash'],
        'qr_code': qr_filename,
        'receipt_path': receipt_path
    }

    return redirect(url_for('voter.receipt'))

@voter_bp.route('/receipt')
def receipt():
    if 'receipt_data' not in session:
        flash('No vote receipt available', 'error')
        return redirect(url_for('voter.dashboard'))
    
    return render_template('voter/receipt.html', receipt=session['receipt_data'])