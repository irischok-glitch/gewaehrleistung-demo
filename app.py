from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'demo-secret-key-change-me')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FILE'] = 'data/claims.json'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# E-Mail Konfiguration (über Umgebungsvariablen)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.office365.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'irinawuckert@outlook.de')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'irina.wuckert@alzura.com')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to_email, subject, body):
    """Sendet eine E-Mail. Schlägt still fehl, wenn keine SMTP-Daten hinterlegt sind."""
    if not SMTP_PASSWORD or not to_email:
        print(f"[E-Mail nicht gesendet] An: {to_email} | Betreff: {subject}")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[E-Mail gesendet] An: {to_email}")
        return True
    except Exception as e:
        print(f"[E-Mail Fehler] {type(e).__name__}: {e}")
        return False

def load_claims():
    if os.path.exists(app.config['DATA_FILE']):
        with open(app.config['DATA_FILE'], 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_claims(claims):
    with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
        json.dump(claims, f, ensure_ascii=False, indent=2)

STATUSES = [
    "Eingegangen",
    "In Prüfung",
    "Unterlagen unvollständig",
    "Artikel abholen",
    "Artikel eingegangen",
    "An Hersteller weitergeschickt",
    "Beim Hersteller",
    "Ausgezahlt",
    "Abgelehnt"
]

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    claims = load_claims()
    
    claim_id = str(uuid.uuid4())[:8].upper()
    auftragsnummer = request.form.get('auftragsnummer', 'UNKNOWN')
    kundennummer = request.form.get('kundennummer', 'UNKNOWN')
    firmenname = request.form.get('firmenname', 'Unbekannt')
    
    folder_name = f"{kundennummer}_{secure_filename(firmenname)}"
    claim_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(claim_folder, exist_ok=True)
    
    documents = []
    
    # Ersteinbaurechnung
    if 'ersteinbau' in request.files:
        file = request.files['ersteinbau']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"Ersteinbaurechnung_{auftragsnummer}.{ext}"
            file.save(os.path.join(claim_folder, filename))
            documents.append({"type": "Ersteinbaurechnung", "filename": filename})
    
    # Kostenaufstellung
    if 'kostenaufstellung' in request.files:
        file = request.files['kostenaufstellung']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"Kostenaufstellung_{auftragsnummer}.{ext}"
            file.save(os.path.join(claim_folder, filename))
            documents.append({"type": "Kostenaufstellung", "filename": filename})
    
    # Diagnoseprotokoll
    if 'diagnose' in request.files:
        file = request.files['diagnose']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"Diagnoseprotokoll_{auftragsnummer}.{ext}"
            file.save(os.path.join(claim_folder, filename))
            documents.append({"type": "Diagnoseprotokoll", "filename": filename})
    
    # Fotos (up to 3)
    for i in range(1, 4):
        key = f'foto{i}'
        if key in request.files:
            file = request.files[key]
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"Foto{i}_{auftragsnummer}.{ext}"
                file.save(os.path.join(claim_folder, filename))
                documents.append({"type": f"Foto {i}", "filename": filename})
    
    claim = {
        "id": claim_id,
        "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "status": "Eingegangen",
        "folder": folder_name,
        "documents": documents,
        "comments": [],
        "chat": [],
        "tracking_number": "",
        "form_data": dict(request.form)
    }
    
    claims.append(claim)
    save_claims(claims)
    
    # Bestätigungs-E-Mail an den Kunden (darf den Antrag nicht blockieren)
    try:
        customer_email = request.form.get('email', '')
        if customer_email:
            subject = f"Gewährleistungsantrag eingegangen – {auftragsnummer}"
            body = f"""Guten Tag,

Ihr Gewährleistungsantrag wurde erfolgreich übermittelt.

Antragsnummer: {claim_id}
Auftragsnummer: {auftragsnummer}
Firmenname: {firmenname}

Wir prüfen Ihren Antrag und melden uns bei Ihnen, sobald es Neuigkeiten gibt.

Mit freundlichen Grüßen
ALZURA AG – Gewährleistung
"""
            send_email(customer_email, subject, body)
    except Exception as e:
        print(f"[E-Mail Block Fehler] {e}")
    
    return redirect(url_for('success', claim_id=claim_id))

@app.route('/success/<claim_id>')
def success(claim_id):
    return render_template('success.html', claim_id=claim_id)

@app.route('/backoffice')
def backoffice():
    claims = load_claims()
    return render_template('backoffice.html', claims=claims, statuses=STATUSES)

@app.route('/backoffice/<claim_id>')
def claim_detail(claim_id):
    claims = load_claims()
    claim = next((c for c in claims if c['id'] == claim_id), None)
    if not claim:
        return "Antrag nicht gefunden", 404
    return render_template('detail.html', claim=claim, statuses=STATUSES)

@app.route('/update_status/<claim_id>', methods=['POST'])
def update_status(claim_id):
    claims = load_claims()
    claim = next((c for c in claims if c['id'] == claim_id), None)
    if claim:
        new_status = request.form.get('status')
        comment = request.form.get('comment', '')
        tracking = request.form.get('tracking_number', '')
        
        claim['status'] = new_status
        if tracking:
            claim['tracking_number'] = tracking
        if comment:
            claim['comments'].append({
                "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "text": comment,
                "internal": True
            })
        save_claims(claims)
        
        # Status-E-Mail an den Kunden
        customer_email = claim.get('form_data', {}).get('email', '')
        if customer_email and new_status and new_status != 'Eingegangen':
            auftragsnummer = claim.get('form_data', {}).get('auftragsnummer', '')
            subject = f"Statusupdate zu Ihrem Gewährleistungsantrag – {auftragsnummer}"
            body = f"""Guten Tag,

der Status Ihres Gewährleistungsantrags hat sich geändert.

Antragsnummer: {claim_id}
Neuer Status: {new_status}
"""
            if tracking:
                body += f"Sendungsnummer: {tracking}\n"
            body += """
Bei Rückfragen antworten Sie bitte auf diese E-Mail.

Mit freundlichen Grüßen
ALZURA AG – Gewährleistung
"""
            send_email(customer_email, subject, body)
    
    return redirect(url_for('claim_detail', claim_id=claim_id))

@app.route('/add_chat/<claim_id>', methods=['POST'])
def add_chat(claim_id):
    claims = load_claims()
    claim = next((c for c in claims if c['id'] == claim_id), None)
    if claim:
        message = request.form.get('message', '')
        if message:
            claim['chat'].append({
                "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "sender": "Mitarbeiter",
                "text": message
            })
            save_claims(claims)
    return redirect(url_for('claim_detail', claim_id=claim_id))

@app.route('/uploads/<path:folder>/<path:filename>')
def download_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
