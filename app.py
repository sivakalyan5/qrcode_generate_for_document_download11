import os
import sqlite3
import uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename
import qrcode

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_FOLDER", DATA_DIR / "uploads"))
QR_DIR = Path(os.environ.get("QR_FOLDER", DATA_DIR / "qrcodes"))
DB_PATH = os.environ.get("DATABASE_PATH", str(DATA_DIR / "documents.db"))

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "jpg", "jpeg", "png"}
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "20"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

for folder in (DATA_DIR, UPLOAD_DIR, QR_DIR):
    Path(folder).mkdir(parents=True, exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def public_base_url():
    # Set PUBLIC_BASE_URL to your deployed HTTPS URL for reliable QR codes.
    return os.environ.get("PUBLIC_BASE_URL", request.host_url.rstrip("/")).rstrip("/")

@app.route("/", methods=["GET"])
def index():
    with db() as conn:
        documents = conn.execute(
            "SELECT id, original_name, uploaded_at FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
    return render_template("index.html", documents=documents)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("document")
    if not file or not file.filename:
        flash("Please choose a document first.", "error")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("That file type is not allowed.", "error")
        return redirect(url_for("index"))

    doc_id = uuid.uuid4().hex
    original_name = secure_filename(file.filename) or "document"
    extension = Path(original_name).suffix.lower()
    stored_name = f"{doc_id}{extension}"
    file.save(UPLOAD_DIR / stored_name)

    with db() as conn:
        conn.execute(
            "INSERT INTO documents (id, original_name, stored_name) VALUES (?, ?, ?)",
            (doc_id, original_name, stored_name)
        )

    download_url = f"{public_base_url()}{url_for('download', doc_id=doc_id)}"
    qr = qrcode.QRCode(box_size=9, border=3)
    qr.add_data(download_url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(QR_DIR / f"{doc_id}.png")

    flash("Document uploaded and QR code created.", "success")
    return redirect(url_for("document_detail", doc_id=doc_id))

@app.route("/document/<doc_id>")
def document_detail(doc_id):
    with db() as conn:
        document = conn.execute(
            "SELECT id, original_name, uploaded_at FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
    if not document:
        abort(404)
    download_url = f"{public_base_url()}{url_for('download', doc_id=doc_id)}"
    return render_template("document.html", document=document, download_url=download_url)

@app.route("/qr/<doc_id>.png")
def qr_image(doc_id):
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM documents WHERE id = ?", (doc_id,)).fetchone()
    if not exists:
        abort(404)
    return send_from_directory(QR_DIR, f"{doc_id}.png", mimetype="image/png")

@app.route("/download/<doc_id>")
def download(doc_id):
    with db() as conn:
        document = conn.execute(
            "SELECT original_name, stored_name FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
    if not document:
        abort(404)
    return send_from_directory(
        UPLOAD_DIR, document["stored_name"],
        as_attachment=True, download_name=document["original_name"]
    )

@app.errorhandler(413)
def too_large(_error):
    flash(f"File is too large. Maximum size is {MAX_UPLOAD_MB} MB.", "error")
    return redirect(url_for("index"))

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
