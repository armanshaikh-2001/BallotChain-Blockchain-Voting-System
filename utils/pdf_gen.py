from fpdf import FPDF
from datetime import datetime
import os

def generate_results_pdf(election, candidates, total_voters, voted, turnout):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, "Election Results Report", 0, 1, 'C')
    pdf.ln(10)
    
    # Election info
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Election Name: {election['name'] if election else 'N/A'}", 0, 1)
    pdf.cell(0, 10, f"Start Time: {election['start_time'] if election else 'N/A'}", 0, 1)
    pdf.cell(0, 10, f"End Time: {election['end_time'] if election else 'N/A'}", 0, 1)
    pdf.ln(10)
    
    # Statistics
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Voting Statistics", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Total Voters: {total_voters}", 0, 1)
    pdf.cell(0, 10, f"Votes Cast: {voted}", 0, 1)
    pdf.cell(0, 10, f"Turnout: {turnout:.2f}%", 0, 1)
    pdf.ln(10)
    
    # Results table
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Candidate Results", 0, 1)
    
    # Table header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Candidate", 1, 0, 'C')
    pdf.cell(40, 10, "Party", 1, 0, 'C')
    pdf.cell(30, 10, "Votes", 1, 0, 'C')
    pdf.cell(40, 10, "Percentage", 1, 1, 'C')
    
    # Table rows
    pdf.set_font("Arial", '', 12)
    for candidate in candidates:
        pdf.cell(80, 10, candidate['name'], 1)
        pdf.cell(40, 10, candidate['party'], 1, 0, 'C')
        pdf.cell(30, 10, str(candidate['votes']), 1, 0, 'C')
        pdf.cell(40, 10, f"{candidate['percentage']:.2f}%", 1, 1, 'C')
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, 'C')
    
    # Save file
    os.makedirs('static/receipts', exist_ok=True)
    filename = f"static/receipts/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def generate_voter_receipt(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, "Voting Receipt", 0, 1, 'C')
    pdf.ln(10)
    
    # Voter info
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Voter ID: {data['voter_id']}", 0, 1)
    pdf.cell(0, 10, f"Voter Name: {data['voter_name']}", 0, 1)
    pdf.ln(5)
    
    # Vote info
    pdf.cell(0, 10, f"Candidate: {data['candidate_name']}", 0, 1)
    pdf.cell(0, 10, f"Party: {data['candidate_party']}", 0, 1)
    pdf.cell(0, 10, f"Timestamp: {data['timestamp']}", 0, 1)
    pdf.ln(5)
    
    # Blockchain info
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Blockchain Hash: {data['block_hash']}", 0, 1)
    pdf.ln(10)
    
    # QR Code
    if os.path.exists(data['qr_code']):
        pdf.image(data['qr_code'], x=70, w=70)
        pdf.ln(5)
        pdf.cell(0, 10, "Scan to verify your vote", 0, 1, 'C')
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "This receipt is your proof of voting. Keep it safe.", 0, 0, 'C')
    
    # Save file
    os.makedirs('static/receipts', exist_ok=True)
    filename = f"static/receipts/receipt_{data['voter_id']}.pdf"
    pdf.output(filename)
    return filename