# Blockchain-Based Evidence Preservation System

## Project Overview
The **Blockchain-Based Evidence Preservation System** is a web-based law enforcement application designed to securely manage, track, and verify physical evidence collected during criminal investigations in **Tamil Nadu**. It allows authorized officers—including Police, Forensic Staff, and Evidence Room Officers—to log, amend, and audit evidence records while protecting data integrity using blockchain technology. 

Each evidence entry is linked using SHA-256 cryptographic hashes, making any unauthorized modification instantly detectable. The public can independently verify the chain of custody through a dedicated Public Ledger Lookup portal, while internal access is restricted to authorized personnel through a hidden, role-based authentication gateway[cite: 1].

---

## Software Used

| Software | Purpose |
| :--- | :--- |
| **Python 3.x**[cite: 1] | Backend Language[cite: 1] |
| **Flask**[cite: 1] | Web Framework[cite: 1] |
| **SQLite**[cite: 1] | Database Management[cite: 1] |
| **SQLAlchemy**[cite: 1] | Database ORM[cite: 1] |
| **Flask-Login**[cite: 1] | User Session and Authentication[cite: 1] |
| **Werkzeug**[cite: 1] | Password Hashing and File Utilities[cite: 1] |
| **HTML/CSS**[cite: 1] | Frontend Structure and Styling[cite: 1] |
| **Bootstrap 5**[cite: 1] | Responsive UI Framework[cite: 1] |
| **JavaScript**[cite: 1] | Client-Side Interactivity[cite: 1] |
| **SHA-256**[cite: 1] | Blockchain Hashing Algorithm[cite: 1] |
| **Font Awesome**[cite: 1] | Icon Library[cite: 1] |

---

## Project Modules

1. **Public Ledger Lookup (Landing Page)**[cite: 1]
   * Open to citizens, lawyers, and third-party auditors[cite: 1].
   * Search by Case ID, keyword, Tamil Nadu district, or date range[cite: 1].
   * Displays chain of custody, block history, and cryptographic hashes[cite: 1].
   * No authentication required[cite: 1].

2. **Hidden Authentication Module**[cite: 1]
   * Login page accessible only via secret URL: `/secure-gateway-7741`[cite: 1].
   * Not linked anywhere publicly; only known to authorized personnel[cite: 1].
   * Role-based access: Admin, Forensic Staff, Evidence Room Officer, Police[cite: 1].
   * Quick-fill credential panel for authorized users[cite: 1].

3. **Registry Dashboard**[cite: 1]
   * All logged evidence in a sortable table[cite: 1].
   * Shows Case ID, thumbnail, description, district, measurements, event type, custodian[cite: 1].
   * Filter by keyword, Tamil Nadu district dropdown, and date-from/date-to range[cite: 1].
   * Role-based action buttons (Log Evidence, Correct Evidence)[cite: 1].

4. **Evidence Logging Module (INITIAL Block)**[cite: 1]
   * Register new evidence with auto-generated Case ID (`EV-XXXXXXXX`)[cite: 1].
   * Fields: description, quantity, size/weight, seizure district[cite: 1].
   * Upload image or document attachment (JPG, PNG, PDF, DOCX, etc.)[cite: 1].
   * Entry is cryptographically signed and appended to the blockchain ledger[cite: 1].

5. **Evidence Correction Module (CORRECTION Block)**[cite: 1]
   * Submit a court-order-backed amendment to an existing evidence record[cite: 1].
   * Requires mandatory Court Order Reference Number[cite: 1].
   * Appends a new correction block; original block remains permanently unchanged[cite: 1].
   * Optionally replace the attached file[cite: 1].

6. **Blockchain Module**[cite: 1]
   * Creates Genesis Block on system initialization[cite: 1].
   * Every block contains: Evidence ID, Block Type, Description, Count, Size, District, Officer Details, Court Order, Correction Notes, Attached File, Timestamp, Hashes[cite: 1].
   * Chained: each block's `previous_hash` points to the prior block's hash[cite: 1].

7. **Blockchain Verification (Admin Audit Board)**[cite: 1]
   * Recalculates SHA-256 hash for every block in sequence[cite: 1].
   * Verifies each block's `previous_hash` matches the actual prior hash[cite: 1].
   * Detects tampering: any modification invalidates the hash chain[cite: 1].
   * Admin can simulate tampering and restore integrity for demonstration[cite: 1].

8. **Evidence Chain of Custody History**[cite: 1]
   * Full sequential block-by-block audit trail for any evidence item[cite: 1].
   * Displays every INITIAL and CORRECTION event with timestamps, officer details, district, court order references, and cryptographic hashes[cite: 1].

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/Sivaraj-T-hash/blockchain-evidence-preservation-system.git](https://github.com/Sivaraj-T-hash/blockchain-evidence-preservation-system.git)
   cd blockchain-evidence-preservation-system
