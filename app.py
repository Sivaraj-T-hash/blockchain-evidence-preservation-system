import os
import datetime
import hashlib
import uuid
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blockchain-evidence-preservation-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evidence_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret login gateway path - only authorized persons should know this
SECRET_LOGIN_PATH = '/secure-gateway-7741'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'secret_login'
login_manager.login_message_category = 'info'

# All 38 Tamil Nadu districts
TN_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Kanniyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Villupuram", "Virudhunagar"
]

# --- MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    badge_number = db.Column(db.String(30), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class EvidenceBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.String(50), nullable=False)
    block_type = db.Column(db.String(30), nullable=False)   # INITIAL, CORRECTION
    item_description = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(100), nullable=True)     # Tamil Nadu district
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    officer_details = db.Column(db.String(150), nullable=False)

    # Correction specific fields
    court_order_number = db.Column(db.String(100), nullable=True)
    correction_notes = db.Column(db.Text, nullable=True)

    # File attachment
    evidence_file = db.Column(db.String(255), nullable=True)
    evidence_file_type = db.Column(db.String(50), nullable=True)

    # Blockchain links
    previous_hash = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(64), nullable=False)

    def calculate_block_hash(self):
        ts_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        data_string = (
            f"{self.evidence_id}|"
            f"{self.block_type}|"
            f"{self.item_description}|"
            f"{self.count}|"
            f"{self.size}|"
            f"{self.district or ''}|"
            f"{ts_str}|"
            f"{self.officer_details}|"
            f"{self.court_order_number or ''}|"
            f"{self.correction_notes or ''}|"
            f"{self.evidence_file or ''}|"
            f"{self.evidence_file_type or ''}|"
            f"{self.previous_hash}"
        )
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- HELPER FUNCTIONS ---

def create_genesis_block():
    genesis = EvidenceBlock(
        evidence_id="SYSTEM-GENESIS",
        block_type="SYSTEM",
        item_description="Genesis block of the evidence preservation ledger.",
        count=0,
        size="0",
        district="",
        timestamp=datetime.datetime(2026, 1, 1, 0, 0, 0),
        officer_details="SYSTEM",
        court_order_number="",
        correction_notes="",
        evidence_file="",
        evidence_file_type="",
        previous_hash="0"
    )
    genesis.hash = genesis.calculate_block_hash()
    db.session.add(genesis)
    db.session.commit()
    return genesis

def get_latest_block():
    latest = EvidenceBlock.query.order_by(EvidenceBlock.id.desc()).first()
    if not latest:
        latest = create_genesis_block()
    return latest

def add_new_block(evidence_id, block_type, item_description, count, size, officer,
                  district=None, court_order=None, notes=None,
                  evidence_file=None, evidence_file_type=None):
    latest = get_latest_block()
    officer_info = f"{officer.fullname} ({officer.badge_number}) - {officer.role}"
    new_block = EvidenceBlock(
        evidence_id=evidence_id,
        block_type=block_type,
        item_description=item_description,
        count=count,
        size=size,
        district=district,
        timestamp=datetime.datetime.utcnow(),
        officer_details=officer_info,
        court_order_number=court_order,
        correction_notes=notes,
        evidence_file=evidence_file,
        evidence_file_type=evidence_file_type,
        previous_hash=latest.hash
    )
    new_block.hash = new_block.calculate_block_hash()
    db.session.add(new_block)
    db.session.commit()
    return new_block

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'}

def save_uploaded_file(file):
    if not file or file.filename == '':
        return None, None
    if file and allowed_file(file.filename):
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"ev_{uuid.uuid4().hex[:8]}{ext}"
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        file_type = 'other'
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_type = 'image'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx']:
            file_type = 'document'
        return filename, file_type
    return None, None

def build_evidence_list(all_blocks, search_query='', district_filter='', date_from='', date_to=''):
    """Build a list of current evidence states with optional filters."""
    evidence_histories = {}
    for block in all_blocks:
        if block.evidence_id == "SYSTEM-GENESIS":
            continue
        if block.evidence_id not in evidence_histories:
            evidence_histories[block.evidence_id] = []
        evidence_histories[block.evidence_id].append(block)

    results = []
    for ev_id, history in evidence_histories.items():
        latest_block = history[0]
        initial_block = history[-1]
        has_corrections = any(b.block_type == 'CORRECTION' for b in history)

        # --- Text / keyword filter ---
        if search_query:
            q = search_query.lower()
            matched = False
            if q in ev_id.lower():
                matched = True
            else:
                for block in history:
                    if (q in block.item_description.lower()
                            or q in block.officer_details.lower()
                            or (block.court_order_number and q in block.court_order_number.lower())
                            or q == str(block.timestamp.year)):
                        matched = True
                        break
            if not matched:
                continue

        # --- District filter ---
        if district_filter:
            if not any(
                (block.district or '').strip().lower() == district_filter.strip().lower()
                for block in history
            ):
                continue

        # --- Date-from filter (inclusive, applied to initial block) ---
        if date_from:
            try:
                df = datetime.datetime.strptime(date_from, '%Y-%m-%d')
                if initial_block.timestamp.date() < df.date():
                    continue
            except ValueError:
                pass

        # --- Date-to filter (inclusive, applied to latest block) ---
        if date_to:
            try:
                dt = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                if latest_block.timestamp.date() > dt.date():
                    continue
            except ValueError:
                pass

        results.append({
            'evidence_id': ev_id,
            'latest_block': latest_block,
            'history_count': len(history),
            'has_corrections': has_corrections,
            'initial_block': initial_block,
            'history': sorted(history, key=lambda b: b.id)
        })

    return results

def verify_blockchain_integrity():
    blocks = EvidenceBlock.query.order_by(EvidenceBlock.id.asc()).all()
    verification_log = []
    is_compromised = False
    for i, block in enumerate(blocks):
        calculated_hash = block.calculate_block_hash()
        hash_valid = (block.hash == calculated_hash)
        link_valid = True
        if i > 0:
            link_valid = (block.previous_hash == blocks[i-1].hash)
        block_valid = hash_valid and link_valid
        if not block_valid:
            is_compromised = True
        verification_log.append({
            'id': block.id,
            'evidence_id': block.evidence_id,
            'block_type': block.block_type,
            'timestamp': block.timestamp,
            'db_hash': block.hash,
            'calculated_hash': calculated_hash,
            'previous_hash': block.previous_hash,
            'expected_previous': blocks[i-1].hash if i > 0 else "0",
            'hash_valid': hash_valid,
            'link_valid': link_valid,
            'block_valid': block_valid
        })
    return {'is_secure': not is_compromised, 'log': verification_log}

# --- ROUTES ---

@app.route('/')
def index():
    """Public landing — only shows the search portal."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('public_search'))

# Hidden login — only authorized people know this URL
@app.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def secret_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.fullname}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid credentials. Access denied.', 'danger')
    return render_template('login.html')

# Keep /login pointing to secret too (for login_manager redirects)
@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('secret_login', **request.args))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public_search'))

# --- PUBLIC SEARCH (landing page) ---
@app.route('/search')
def public_search():
    query        = request.args.get('query', '').strip()
    district_f   = request.args.get('district', '').strip()
    date_from    = request.args.get('date_from', '').strip()
    date_to      = request.args.get('date_to', '').strip()

    results = []
    has_any_filter = bool(query or district_f or date_from or date_to)

    if has_any_filter:
        all_blocks = EvidenceBlock.query.order_by(EvidenceBlock.timestamp.desc()).all()
        results = build_evidence_list(all_blocks, query, district_f, date_from, date_to)

    return render_template(
        'public_search.html',
        query=query,
        district_filter=district_f,
        date_from=date_from,
        date_to=date_to,
        results=results,
        tn_districts=TN_DISTRICTS,
        has_any_filter=has_any_filter
    )

# --- AUTHENTICATED DASHBOARD ---
@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '').strip()
    district_f   = request.args.get('district', '').strip()
    date_from    = request.args.get('date_from', '').strip()
    date_to      = request.args.get('date_to', '').strip()

    all_blocks = EvidenceBlock.query.order_by(EvidenceBlock.timestamp.desc()).all()
    evidence_list = build_evidence_list(all_blocks, search_query, district_f, date_from, date_to)

    return render_template(
        'dashboard.html',
        evidence_list=evidence_list,
        search_query=search_query,
        district_filter=district_f,
        date_from=date_from,
        date_to=date_to,
        tn_districts=TN_DISTRICTS
    )

@app.route('/evidence/log', methods=['GET', 'POST'])
@login_required
def log_evidence():
    if current_user.role not in ['Police', 'Forensic Staff', 'Evidence Room Officer']:
        flash('Unauthorized access to logging evidence.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        item_description = request.form.get('item_description')
        count            = request.form.get('count', type=int)
        size             = request.form.get('size')
        district         = request.form.get('district', '').strip()
        evidence_file    = request.files.get('evidence_file')
        if not item_description or count is None or not size:
            flash('Please fill out all required fields.', 'warning')
        else:
            filename, file_type = save_uploaded_file(evidence_file)
            evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
            add_new_block(
                evidence_id=evidence_id,
                block_type='INITIAL',
                item_description=item_description,
                count=count,
                size=size,
                district=district or None,
                officer=current_user,
                evidence_file=filename,
                evidence_file_type=file_type
            )
            flash(f'Evidence {evidence_id} logged and appended to the ledger.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('log_evidence.html', tn_districts=TN_DISTRICTS)

@app.route('/evidence/correct/<evidence_id>', methods=['GET', 'POST'])
@login_required
def request_correction(evidence_id):
    if current_user.role not in ['Police', 'Forensic Staff', 'Evidence Room Officer']:
        flash('Unauthorized access to correct evidence.', 'danger')
        return redirect(url_for('dashboard'))
    history = EvidenceBlock.query.filter_by(evidence_id=evidence_id).order_by(EvidenceBlock.id.asc()).all()
    if not history:
        flash('Evidence record not found.', 'danger')
        return redirect(url_for('dashboard'))
    latest_state = history[-1]
    if request.method == 'POST':
        item_description   = request.form.get('item_description')
        count              = request.form.get('count', type=int)
        size               = request.form.get('size')
        district           = request.form.get('district', '').strip()
        court_order_number = request.form.get('court_order_number')
        correction_notes   = request.form.get('correction_notes')
        evidence_file      = request.files.get('evidence_file')
        if not court_order_number:
            flash('A valid Court Order reference number is mandatory.', 'danger')
        elif not item_description or count is None or not size or not correction_notes:
            flash('Please fill out all fields.', 'warning')
        else:
            filename, file_type = save_uploaded_file(evidence_file)
            if not filename and latest_state.evidence_file:
                filename  = latest_state.evidence_file
                file_type = latest_state.evidence_file_type
            add_new_block(
                evidence_id=evidence_id,
                block_type='CORRECTION',
                item_description=item_description,
                count=count,
                size=size,
                district=district or latest_state.district,
                officer=current_user,
                court_order=court_order_number,
                notes=correction_notes,
                evidence_file=filename,
                evidence_file_type=file_type
            )
            flash(f'Corrective block for {evidence_id} appended to the ledger.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('request_correction.html', evidence=latest_state, tn_districts=TN_DISTRICTS)

@app.route('/evidence/history/<evidence_id>')
@login_required
def evidence_history(evidence_id):
    history = EvidenceBlock.query.filter_by(evidence_id=evidence_id).order_by(EvidenceBlock.id.asc()).all()
    if not history:
        flash('Evidence record not found.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('evidence_history.html', history=history, evidence_id=evidence_id)

@app.route('/admin/audit')
@login_required
def admin_audit():
    if current_user.role != 'Admin':
        flash('Unauthorized access to administrative audit board.', 'danger')
        return redirect(url_for('dashboard'))
    integrity_status = verify_blockchain_integrity()
    return render_template('audit.html', status=integrity_status)

# --- DEBUG/DEMONSTRATION ROUTES ---

@app.route('/admin/tamper', methods=['POST'])
@login_required
def admin_tamper():
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    target_block = EvidenceBlock.query.filter(EvidenceBlock.evidence_id != 'SYSTEM-GENESIS').first()
    if not target_block:
        return jsonify({'error': 'No evidence to tamper with. Log some evidence first!'}), 400
    target_block.item_description = "[UNAUTHORIZED ACCESS] Tampered Item Description"
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'Tampering simulated on Block ID {target_block.id} (Evidence ID {target_block.evidence_id}). Blockchain verification will detect this!',
        'block_id': target_block.id
    })

@app.route('/admin/restore', methods=['POST'])
@login_required
def admin_restore():
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    blocks = EvidenceBlock.query.order_by(EvidenceBlock.id.asc()).all()
    for i, block in enumerate(blocks):
        block.previous_hash = blocks[i-1].hash if i > 0 else "0"
        block.hash = block.calculate_block_hash()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Blockchain integrity restored.'})

# --- SEEDING DATABASE ---

def seed_database():
    db.create_all()

    if not User.query.first():
        # Real Tamil names as requested
        admin = User(username='sivaraj', fullname='Sivaraj T', badge_number='AD-001', role='Admin')
        admin.set_password('sivaraj123')

        forensic = User(username='jeffy', fullname='Jeffy R', badge_number='FS-002', role='Forensic Staff')
        forensic.set_password('jeffy123')

        officer = User(username='vignesh', fullname='Vignesh K', badge_number='EO-003', role='Evidence Room Officer')
        officer.set_password('vignesh123')

        police = User(username='meena', fullname='Meena S', badge_number='PL-004', role='Police')
        police.set_password('meena123')

        db.session.add_all([admin, forensic, officer, police])
        db.session.commit()

    if not EvidenceBlock.query.first():
        create_genesis_block()

        def seed_block(evidence_id, block_type, item_description, count, size,
                       officer_name, officer_badge, officer_role, timestamp,
                       district=None, court_order=None, notes=None,
                       evidence_file=None, evidence_file_type=None):
            latest = EvidenceBlock.query.order_by(EvidenceBlock.id.desc()).first()
            officer_info = f"{officer_name} ({officer_badge}) - {officer_role}"
            new_block = EvidenceBlock(
                evidence_id=evidence_id,
                block_type=block_type,
                item_description=item_description,
                count=count,
                size=size,
                district=district,
                timestamp=timestamp,
                officer_details=officer_info,
                court_order_number=court_order,
                correction_notes=notes,
                evidence_file=evidence_file,
                evidence_file_type=evidence_file_type,
                previous_hash=latest.hash
            )
            new_block.hash = new_block.calculate_block_hash()
            db.session.add(new_block)
            db.session.commit()
            return new_block

        now = datetime.datetime.utcnow()

        # 1. Lenovo ThinkPad — Chennai
        seed_block(
            evidence_id="EV-8FA32C9E", block_type="INITIAL",
            item_description="One black Lenovo ThinkPad L14 laptop, serial number #L3-N9872F. Confiscated from suspect's office at Anna Salai, Chennai. Contains digital forensics analysis logs of the target server.",
            count=1, size="1.6kg, 33cm x 23cm", district="Chennai",
            officer_name="Meena S", officer_badge="PL-004", officer_role="Police",
            timestamp=now - datetime.timedelta(days=30),
            evidence_file="sample_laptop.png", evidence_file_type="image"
        )

        # 2. USD Cash — Coimbatore
        seed_block(
            evidence_id="EV-5B92C1D4", block_type="INITIAL",
            item_description="Sealed plastic container holding 12 bundles of USD currency ($100 bills), totaling $120,000. Recovered from suspect's commercial vault in Gandhipuram, Coimbatore.",
            count=12, size="3.2kg, 30cm x 20cm x 15cm", district="Coimbatore",
            officer_name="Vignesh K", officer_badge="EO-003", officer_role="Evidence Room Officer",
            timestamp=now - datetime.timedelta(days=28),
            evidence_file="sample_cash.png", evidence_file_type="image"
        )

        # 3. Glock Pistol — Madurai
        seed_block(
            evidence_id="EV-2F10B8D9", block_type="INITIAL",
            item_description="Caliber 9mm Glock 19 semi-automatic pistol, serial number #GP8419, with one empty magazine. Recovered from vehicle trunk near Meenakshi Amman Temple area, Madurai.",
            count=1, size="670g, 18.7cm long", district="Madurai",
            officer_name="Meena S", officer_badge="PL-004", officer_role="Police",
            timestamp=now - datetime.timedelta(days=26),
            evidence_file="sample_glock.png", evidence_file_type="image"
        )

        # 4. Apple iPhone — Salem
        seed_block(
            evidence_id="EV-7D1E8F40", block_type="INITIAL",
            item_description="One black Apple iPhone 14 Pro, model A2890, IMEI: 358902110294812, cracked rear glass panel. Secured in static-shielding bag. Seized in Salem city market area.",
            count=1, size="206g, 14.7cm x 7.1cm", district="Salem",
            officer_name="Jeffy R", officer_badge="FS-002", officer_role="Forensic Staff",
            timestamp=now - datetime.timedelta(days=25),
            evidence_file="sample_phone.png", evidence_file_type="image"
        )

        # 5. iPhone Correction — Salem
        seed_block(
            evidence_id="EV-7D1E8F40", block_type="CORRECTION",
            item_description="One black Apple iPhone 14 Pro, model A2890, IMEI: 358902110294812, cracked rear glass panel. Released to Forensics Lab B for chip-off database dump.",
            count=1, size="206g, 14.7cm x 7.1cm", district="Salem",
            officer_name="Jeffy R", officer_badge="FS-002", officer_role="Forensic Staff",
            timestamp=now - datetime.timedelta(days=24),
            court_order="CO-2026-904A",
            notes="Authorized release to forensic team for extraction of secure messenger databases.",
            evidence_file="sample_phone.png", evidence_file_type="image"
        )

        # 6. Transaction logs — Trichy
        seed_block(
            evidence_id="EV-4E2C7B1A", block_type="INITIAL",
            item_description="Hard copy printouts of encrypted transaction logs (142 pages) bound in a black leather folder. Marked as Exhibit D. Seized from Cantonment area, Tiruchirappalli.",
            count=1, size="820g, A4 size, 4cm thick", district="Tiruchirappalli",
            officer_name="Vignesh K", officer_badge="EO-003", officer_role="Evidence Room Officer",
            timestamp=now - datetime.timedelta(days=22),
            evidence_file="sample_document.png", evidence_file_type="image"
        )

        # 7. USB Flash Drive — Tirunelveli
        seed_block(
            evidence_id="EV-9C3D2F8B", block_type="INITIAL",
            item_description="SanDisk Ultra 128GB USB 3.0 flash drive, red/black casing. Contains CCTV surveillance video files from parking garage camera #5 in Tirunelveli.",
            count=1, size="10g, 5.6cm long", district="Tirunelveli",
            officer_name="Jeffy R", officer_badge="FS-002", officer_role="Forensic Staff",
            timestamp=now - datetime.timedelta(days=19),
        )

        # 8. External Hard Drive — Vellore
        seed_block(
            evidence_id="EV-3F4D5E6F", block_type="INITIAL",
            item_description="One silver Seagate Backup Plus 2TB external portable hard drive, serial number #NA9K12L4, with USB cable. Confiscated from IT office in Katpadi, Vellore.",
            count=1, size="159g, 11cm x 8cm", district="Vellore",
            officer_name="Meena S", officer_badge="PL-004", officer_role="Police",
            timestamp=now - datetime.timedelta(days=15),
        )

        # 9. Blood sample — Erode
        seed_block(
            evidence_id="EV-1A8B9C2D", block_type="INITIAL",
            item_description="Sealed blood collection tube for DNA analysis, labeled #DNA-992-X. Stored at 4°C. Sample collected from suspect in Erode district during arrest.",
            count=1, size="45g, 10ml tube", district="Erode",
            officer_name="Jeffy R", officer_badge="FS-002", officer_role="Forensic Staff",
            timestamp=now - datetime.timedelta(days=12),
        )

        # 10. DSLR Camera — Thanjavur
        seed_block(
            evidence_id="EV-8E9F0A1B", block_type="INITIAL",
            item_description="Digital SLR Camera Canon EOS Rebel T7, black, serial number #C3384210, with 18-55mm lens and 32GB SD card containing crime scene photographs from Thanjavur.",
            count=1, size="475g body, 13cm x 10cm", district="Thanjavur",
            officer_name="Vignesh K", officer_badge="EO-003", officer_role="Evidence Room Officer",
            timestamp=now - datetime.timedelta(days=8),
        )

        # 11. Counterfeit Gold Bar — Dindigul
        seed_block(
            evidence_id="EV-6F7E8D9C", block_type="INITIAL",
            item_description="One counterfeit gold bar, stamped 999.9 Fine Gold 100g, Serial #AU-99218. Recovered from mail fraud distribution suspect in Dindigul.",
            count=1, size="100g, 4.5cm x 2.5cm", district="Dindigul",
            officer_name="Vignesh K", officer_badge="EO-003", officer_role="Evidence Room Officer",
            timestamp=now - datetime.timedelta(days=4),
        )

        # 12. DSLR Camera Correction — Thanjavur
        seed_block(
            evidence_id="EV-8E9F0A1B", block_type="CORRECTION",
            item_description="Digital SLR Camera Canon EOS Rebel T7, black, serial number #C3384210, with 18-55mm lens. Corrected: 64GB Lexar SD card found inside, not 32GB as initially logged.",
            count=1, size="475g body, 13cm x 10cm", district="Thanjavur",
            officer_name="Vignesh K", officer_badge="EO-003", officer_role="Evidence Room Officer",
            timestamp=now - datetime.timedelta(days=1),
            court_order="CO-2026-905B",
            notes="Correction of SD card capacity error from initial registry block, validated by evidence room inspector.",
        )

if __name__ == '__main__':
    with app.app_context():
        seed_database()
    app.run(debug=True)
