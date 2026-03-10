from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import sqlite3, os, json, hashlib, secrets
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='../public', static_url_path='')
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/bookings.db')

# ── CONFIG (edit these) ──────────────────────────────────────────────────────
CONFIG = {
    "studio_name":   "Neha Ahluwalia Artistry",
    "studio_phone":  "+917082256996",
    "studio_email":  "nehaahluwaliaartistry@gmail.com",   # studio's email
    "admin_email":   "nehaahluwaliaartistry@gmail.com",   # gets booking alerts
    "smtp_host":     "smtp.gmail.com",
    "smtp_port":     587,
    "smtp_user":     "",          # fill: Gmail address for sending
    "smtp_pass":     "",          # fill: Gmail app password
    "whatsapp_api":  "twilio",    # 'twilio' or 'none'
    "twilio_sid":    "",          # fill: Twilio Account SID
    "twilio_token":  "",          # fill: Twilio Auth Token
    "twilio_from":   "",          # fill: Twilio WhatsApp number e.g. whatsapp:+14155238886
    "admin_wa":      "whatsapp:+917082256996",
    "admin_password_hash": hashlib.sha256("admin@neha2026".encode()).hexdigest()
}
# ────────────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS bookings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            email       TEXT,
            service     TEXT NOT NULL,
            date        TEXT NOT NULL,
            time_slot   TEXT NOT NULL,
            message     TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            phone       TEXT NOT NULL,
            email       TEXT,
            message     TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    db.commit()
    db.close()

def send_email(to, subject, html_body):
    if not CONFIG["smtp_user"] or not CONFIG["smtp_pass"]:
        print(f"[EMAIL SKIPPED - not configured] To: {to} | Subject: {subject}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = CONFIG["smtp_user"]
        msg["To"]      = to
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(CONFIG["smtp_host"], CONFIG["smtp_port"]) as s:
            s.starttls()
            s.login(CONFIG["smtp_user"], CONFIG["smtp_pass"])
            s.sendmail(CONFIG["smtp_user"], to, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_whatsapp(to, message):
    if not CONFIG["twilio_sid"] or not CONFIG["twilio_token"]:
        print(f"[WHATSAPP SKIPPED - not configured] To: {to} | Msg: {message[:60]}")
        return False
    try:
        from twilio.rest import Client
        client = Client(CONFIG["twilio_sid"], CONFIG["twilio_token"])
        client.messages.create(body=message, from_=CONFIG["twilio_from"], to=to)
        return True
    except Exception as e:
        print(f"[WHATSAPP ERROR] {e}")
        return False

def notify_booking(booking):
    # ── Email to admin ──
    admin_html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:auto;background:#0D0B09;color:#FAF6EF;padding:40px;border:1px solid #C9A84C;">
      <h2 style="color:#C9A84C;font-weight:300;letter-spacing:2px;">NEW BOOKING REQUEST</h2>
      <hr style="border-color:#C9A84C;opacity:0.3;">
      <table style="width:100%;margin-top:20px;font-size:14px;line-height:2;">
        <tr><td style="color:#C9A84C;width:140px;">Name</td><td>{booking['name']}</td></tr>
        <tr><td style="color:#C9A84C;">Phone</td><td>{booking['phone']}</td></tr>
        <tr><td style="color:#C9A84C;">Email</td><td>{booking.get('email') or '—'}</td></tr>
        <tr><td style="color:#C9A84C;">Service</td><td>{booking['service']}</td></tr>
        <tr><td style="color:#C9A84C;">Date</td><td>{booking['date']}</td></tr>
        <tr><td style="color:#C9A84C;">Time</td><td>{booking['time_slot']}</td></tr>
        <tr><td style="color:#C9A84C;">Note</td><td>{booking['message'] or '—'}</td></tr>
      </table>
      <p style="margin-top:30px;font-size:12px;color:rgba(250,246,239,0.4);">Neha Ahluwalia Artistry — Booking System</p>
    </div>"""
    send_email(CONFIG["admin_email"], f"New Booking — {booking['name']} | {booking['service']}", admin_html)

    # ── Email to client ──
    if booking.get("email"):
        client_html = f"""
        <div style="font-family:Georgia,serif;max-width:600px;margin:auto;background:#0D0B09;color:#FAF6EF;padding:40px;border:1px solid #C9A84C;">
          <h2 style="color:#C9A84C;font-weight:300;letter-spacing:2px;">BOOKING CONFIRMED</h2>
          <p style="color:rgba(250,246,239,0.7);line-height:1.8;">Thank you {booking['name']}! Your appointment request has been received.</p>
          <hr style="border-color:#C9A84C;opacity:0.3;">
          <table style="width:100%;margin-top:20px;font-size:14px;line-height:2;">
            <tr><td style="color:#C9A84C;width:120px;">Service</td><td>{booking['service']}</td></tr>
            <tr><td style="color:#C9A84C;">Date</td><td>{booking['date']}</td></tr>
            <tr><td style="color:#C9A84C;">Time</td><td>{booking['time_slot']}</td></tr>
          </table>
          <p style="margin-top:24px;color:rgba(250,246,239,0.6);font-size:13px;">We will confirm your slot shortly. For queries, WhatsApp us at <strong style="color:#C9A84C;">+91 70822 56996</strong></p>
          <p style="margin-top:30px;font-size:12px;color:rgba(250,246,239,0.4);">— Neha Ahluwalia Artistry, Kurukshetra</p>
        </div>"""
        send_email(booking["email"], "Your Booking Request — Neha Ahluwalia Artistry", client_html)

    # ── WhatsApp to admin ──
    wa_msg = (f"✨ New Booking!\n\n"
              f"👤 {booking['name']}\n"
              f"📞 {booking['phone']}\n"
              f"💄 {booking['service']}\n"
              f"📅 {booking['date']} at {booking['time_slot']}\n"
              f"📝 {booking.get('message') or 'No note'}")
    send_whatsapp(CONFIG["admin_wa"], wa_msg)

    # ── WhatsApp to client ──
    send_whatsapp(f"whatsapp:{booking['phone']}",
        f"Hi {booking['name']}! 💄 Your booking at Neha Ahluwalia Artistry has been received.\n\n"
        f"Service: {booking['service']}\nDate: {booking['date']} | Time: {booking['time_slot']}\n\n"
        f"We'll confirm shortly. Questions? Reply here! ✨")


# ── PUBLIC ROUTES ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/booking', methods=['POST'])
def create_booking():
    data = request.json or {}
    required = ['name', 'phone', 'service', 'date', 'time_slot']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing: {', '.join(missing)}"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO bookings (name,phone,email,service,date,time_slot,message) VALUES (?,?,?,?,?,?,?)",
        (data['name'], data['phone'], data.get('email',''), data['service'],
         data['date'], data['time_slot'], data.get('message',''))
    )
    db.commit()
    booking_id = cur.lastrowid
    db.close()

    notify_booking({**data, "id": booking_id})
    return jsonify({"ok": True, "message": "Booking received!", "id": booking_id})

@app.route('/api/contact', methods=['POST'])
def create_contact():
    data = request.json or {}
    required = ['name', 'phone', 'message']
    if any(not data.get(f) for f in required):
        return jsonify({"ok": False, "error": "Missing required fields"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO contacts (name,phone,email,message) VALUES (?,?,?,?)",
        (data['name'], data['phone'], data.get('email',''), data['message'])
    )
    db.commit()
    db.close()

    # Notify admin
    send_whatsapp(CONFIG["admin_wa"],
        f"📩 New Contact Message\n👤 {data['name']}\n📞 {data['phone']}\n💬 {data['message'][:200]}")
    send_email(CONFIG["admin_email"], f"New Message — {data['name']}",
        f"<p><b>Name:</b> {data['name']}<br><b>Phone:</b> {data['phone']}<br>"
        f"<b>Email:</b> {data.get('email','—')}<br><b>Message:</b> {data['message']}</p>")

    return jsonify({"ok": True, "message": "Message sent!"})


# ── ADMIN ROUTES ──────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    pw_hash = hashlib.sha256(data.get('password','').encode()).hexdigest()
    if pw_hash == CONFIG["admin_password_hash"]:
        session['admin'] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Invalid password"}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route('/api/admin/bookings', methods=['GET'])
@admin_required
def admin_bookings():
    status = request.args.get('status')
    db = get_db()
    if status and status != 'all':
        rows = db.execute("SELECT * FROM bookings WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
    db.close()
    return jsonify({"ok": True, "bookings": [dict(r) for r in rows]})

@app.route('/api/admin/bookings/<int:bid>', methods=['PATCH'])
@admin_required
def update_booking(bid):
    data = request.json or {}
    status = data.get('status')
    if status not in ('pending', 'confirmed', 'cancelled', 'completed'):
        return jsonify({"ok": False, "error": "Invalid status"}), 400
    db = get_db()
    db.execute("UPDATE bookings SET status=? WHERE id=?", (status, bid))
    db.commit()

    if status == 'confirmed':
        row = db.execute("SELECT * FROM bookings WHERE id=?", (bid,)).fetchone()
        if row:
            b = dict(row)
            send_whatsapp(f"whatsapp:{b['phone']}",
                f"✅ Booking Confirmed!\n\nHi {b['name']}, your appointment is confirmed.\n"
                f"💄 {b['service']}\n📅 {b['date']} at {b['time_slot']}\n\n"
                f"See you soon! — Neha Ahluwalia Artistry ✨")
            if b.get('email'):
                send_email(b['email'], "Booking Confirmed — Neha Ahluwalia Artistry",
                    f"<p>Hi {b['name']}, your <b>{b['service']}</b> appointment on <b>{b['date']}</b> "
                    f"at <b>{b['time_slot']}</b> is confirmed! See you soon. 💄</p>")
    db.close()
    return jsonify({"ok": True})

@app.route('/api/admin/bookings/<int:bid>', methods=['DELETE'])
@admin_required
def delete_booking(bid):
    db = get_db()
    db.execute("DELETE FROM bookings WHERE id=?", (bid,))
    db.commit()
    db.close()
    return jsonify({"ok": True})

@app.route('/api/admin/contacts', methods=['GET'])
@admin_required
def admin_contacts():
    db = get_db()
    rows = db.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    db.close()
    return jsonify({"ok": True, "contacts": [dict(r) for r in rows]})

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    db = get_db()
    total    = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    pending  = db.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'").fetchone()[0]
    confirmed= db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'").fetchone()[0]
    completed= db.execute("SELECT COUNT(*) FROM bookings WHERE status='completed'").fetchone()[0]
    messages = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    recent   = db.execute("SELECT * FROM bookings ORDER BY created_at DESC LIMIT 5").fetchall()
    db.close()
    return jsonify({"ok": True, "stats": {
        "total": total, "pending": pending,
        "confirmed": confirmed, "completed": completed, "messages": messages
    }, "recent": [dict(r) for r in recent]})

if __name__ == '__main__':
    init_db()
    print("✨ Neha Ahluwalia Artistry — Backend running at http://localhost:5000")
    print("   Admin panel: http://localhost:5000/admin.html")
    print("   Default admin password: admin@neha2026")
    app.run(debug=True, port=5000)
