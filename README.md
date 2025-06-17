
# 🗳️ BallotChain - Blockchain Voting System

BallotChain is a **secure, tamper-proof voting system** built with Python and Flask, leveraging a custom blockchain engine to guarantee integrity, transparency, and fairness in digital elections.

---

## 🌟 Features

### 🛠️ Admin Panel
- Create and manage elections with flexible timing
- Add/remove candidates with profile photos and manifestos
- Import voters via CSV/JSON
- Live election stats and graphical turnout insights
- Blockchain explorer for transparency
- Export results to PDF or JSON formats

### 🧑‍💼 Voter Panel
- Secure voter authentication with session control
- Real-time access to candidate information
- One-time vote submission enforced
- Blockchain-verified digital receipt generation
- Downloadable PDF confirmation with embedded QR code

### 🔐 Blockchain Engine
- Proof-of-work enabled tamper detection
- SHA-256 hashing for vote anonymity
- Immutable recording of every cast vote
- Full chain validation to detect tampering

---

## 🗂️ File Structure

```
BallotChain/
├── app.py                  # App bootstrapper
├── blockchain.py           # Blockchain engine
├── auth.py                 # Login handling
├── routes/
│   ├── admin_routes.py     # Admin-specific endpoints
│   └── voter_routes.py     # Voter-specific endpoints
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # Client-side scripts
│   ├── images/             # Candidate images
│   ├── qrcodes/            # Generated QR codes
│   └── receipts/           # PDF receipts
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard_admin.html
│   ├── dashboard_voter.html
│   ├── vote.html
│   └── receipt.html
├── data/
│   ├── blockchain.json     # Vote records
│   ├── voters.json         # Registered voters
│   ├── candidates.json     # Candidate details
│   └── elections.json      # Election metadata
└── utils/
    ├── pdf_gen.py          # Receipt generator
    └── qr_gen.py           # QR code generator
```

---

## 🔁 System Workflow

### 1. ⚙️ Initialization
- App bootstraps via `app.py`
- Creates required directories:
  - `data/`, `static/qrcodes/`, `static/receipts/`
- Initializes empty JSON files
- Registers Flask Blueprints (`auth`, `admin`, `voter`)

---

### 2. 🔐 Authentication Flow
- Users access `/` and see the login form
- Admins are verified with hardcoded credentials
- Voters are authenticated using `voters.json`
- Role-based session management and redirection

---

### 3. 🧑‍💼 Admin Workflow

#### A. Dashboard Access
- Session role checked (`admin`)
- Loads:
  - `elections.json`, `candidates.json`, `voters.json`, `blockchain.json`
- Calculates and displays:
  - Total voters
  - Votes cast
  - Turnout %

#### B. Election Management
- Start/end elections via form
- Validates and updates `elections.json`
- Proof-of-work difficulty can be configured

#### C. Candidate Management
- Add:
  - Form input + image upload
  - Stored in `static/images/` and `candidates.json`
- Delete:
  - Candidate removed, vote record preserved

#### D. Voter Management
- Add manually or import via:
  - CSV: `id,name`
  - JSON: `{"voters": [{"id":"V001","name":"John"}]}`
- Appends to `voters.json` after validation

#### E. Data Export
- Blockchain export: JSON download
- Results export: PDF with charts, metadata, and ranking

---

### 4. 🧑‍⚖️ Voter Workflow

#### A. Voting Process
- Dashboard shows active election or countdown
- Voter selects a candidate
- System:
  - Validates vote
  - Hashes voter ID + timestamp
  - Adds block to `blockchain.json`
  - Marks voter as `has_voted=True`
  - Generates QR receipt and redirects

#### B. Blockchain Handling
- Block includes:
  - Index, timestamp, hashed token, candidate ID, previous hash
- Proof-of-work (difficulty = 4)
- Full chain stored in `blockchain.json`

#### C. Receipt Generation
- QR contains:
  - Hashed voter ID, candidate ID, block hash, timestamp
- PDF includes:
  - Candidate info, timestamp, QR, block data
- Stored in `static/receipts/`

---

## 🚨 Error Handling & Security

### 🔒 Admin
- Prevent duplicate candidates
- Election state validation
- File upload validation with limits

### 🔒 Voter
- No double voting
- 30-minute session timeout
- Chain validity check on app load

---

## 🔐 Security Measures

### ✅ Data Privacy
- Voter IDs are hashed before blockchain insertion
- Receipts anonymized

### ✅ Session Security
- HttpOnly, SameSite cookies
- Flask session protection

### ✅ Validation Checks
- Vote only if:
  - Election active
  - Candidate exists
  - Voter hasn’t voted
- Admin functions protected by session role check

---

## 🛠️ Tech Stack

| Component       | Technology        | Purpose                       |
|----------------|-------------------|-------------------------------|
| **Frontend**    | HTML/CSS/JS       | UI and interaction            |
| **Backend**     | Python + Flask    | Routing and logic             |
| **Database**    | JSON Files        | Lightweight storage           |
| **Blockchain**  | Custom Python     | Proof-of-work & hashing       |
| **PDF**         | `fpdf2`           | Receipt generation            |
| **QR Codes**    | `qrcode`          | Encoded verification          |
| **Auth**        | Flask sessions    | Role-based access             |

---

## 🧭 Typical User Journeys

### 👩‍💼 Admin
1. Login to admin panel
2. Start an election
3. Import voters and add candidates
4. Monitor live votes
5. Export results after ending election

### 🗳️ Voter
1. Login using voter ID
2. View candidates
3. Cast vote (once)
4. Receive receipt with blockchain proof
5. Download and verify receipt

---

## 📄 License

This project is provided for educational and academic purposes. Commercial use is not allowed without prior permission.

---

## 🚀 Get Started

To run the project locally:

```bash
git clone https://github.com/armanshaikh-2001/ballotchain.git
cd ballotchain
pip install -r requirements.txt
python app.py
```

Access via `http://localhost:5000`

---

## 🤝 Contributing

Feel free to fork, improve, and submit PRs! For major changes, please open an issue to discuss.

---
