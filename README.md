# 🔐 Blockchain-Based Evidence Preservation System

A secure web-based law enforcement application that uses **Blockchain (SHA-256)** to preserve the integrity of physical evidence collected during criminal investigations. The system ensures an immutable chain of custody, role-based access control, and public verification of evidence records.

---

## 📌 Features

- 🔗 Blockchain-based evidence storage using SHA-256 hashing
- 🔒 Secure role-based authentication
- 👮 Multiple user roles
  - Police Officer
  - Forensic Staff
  - Evidence Room Officer
  - Administrator
- 📂 Evidence logging with file attachments
- ✏️ Court-order-based evidence correction
- 📜 Complete Chain of Custody tracking
- ✅ Blockchain integrity verification
- 🌐 Public Ledger Lookup Portal
- 📅 Search by
  - Case ID
  - Keywords
  - Tamil Nadu District
  - Date Range
- 📷 Image & Document Upload Support
- 🛡️ Tamper Detection through Blockchain Verification

---

# 🛠️ Tech Stack

### Backend
- Python 3
- Flask

### Database
- SQLite
- SQLAlchemy

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Security
- SHA-256 Blockchain Hashing
- Flask-Login Authentication
- Werkzeug Password Hashing

---

# 📂 Project Modules

## 1. Public Ledger Lookup
Allows citizens, lawyers, and auditors to verify the chain of custody without logging in.

## 2. Secure Authentication
Hidden login gateway with role-based access control.

## 3. Registry Dashboard
View, search, and manage all registered evidence.

## 4. Evidence Logging
Create new blockchain evidence records with attachments.

## 5. Evidence Correction
Append correction blocks backed by court order references while preserving original records.

## 6. Blockchain Engine
Maintains immutable blockchain using SHA-256 cryptographic hashes.

## 7. Blockchain Verification
Automatically detects any tampering by recalculating hashes and verifying block links.

## 8. Evidence History
Displays the complete chain of custody for every evidence item.

---

# 🔒 Blockchain Workflow

Genesis Block
      ↓
Evidence Logged
      ↓
SHA-256 Hash Generated
      ↓
Previous Hash Linked
      ↓
Block Added to Blockchain
      ↓
Blockchain Verification
      ↓
Public Chain Verification

---

# 📷 Screenshots

Add screenshots of:

- Home Page
- Public Search Portal
- Hidden Login Page
- Dashboard
- Log Evidence Page
- Evidence History
- Blockchain Verification
- Evidence Correction Form

---

# 🚀 Installation

```bash
git clone https://github.com/yourusername/blockchain-evidence-preservation-system.git

cd blockchain-evidence-preservation-system
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

# 📁 Project Structure

```
Blockchain-Evidence-Preservation-System/
│
├── static/
├── templates/
├── uploads/
├── app.py
├── requirements.txt
├── README.md
└── evidence_system.db
```

---

# 🔐 Security Features

- SHA-256 Hashing
- Immutable Blockchain Ledger
- Role-Based Access Control
- Secure Password Hashing
- Tamper Detection
- Audit Trail
- Hidden Authentication Gateway

---

# 🎯 Future Enhancements

- QR Code Verification
- Digital Signature Support
- Cloud Storage Integration
- IPFS Support
- Multi-State Deployment
- Mobile Application
- AI-assisted Evidence Classification

---

# 👨‍💻 Author

**Sivaraj T**

🎓 B.Tech Information Technology  
🏫 Velammal Engineering College, Chennai

- GitHub: https://github.com/Sivaraj-T-hash
- LinkedIn: https://www.linkedin.com/in/sivaraj04
- Email: tsivaraj2007@gmail.com

---

# 📄 License

This project is developed for educational and research purposes.

---

## ⭐ If you found this project useful, don't forget to give it a Star!
