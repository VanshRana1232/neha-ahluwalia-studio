# Neha Ahluwalia Artistry — Luxury Salon Website

> A full-stack, image-free luxury website built for a verified bridal makeup artist and beauty influencer based in Kurukshetra, Haryana — featuring an online booking system, admin dashboard, and automated notifications.

---

## 🌐 Live Demo
[Coming Soon — Deploy link here]

---

## ✨ Features

- **Premium UI** — Zero stock images, pure CSS design with gold luxury aesthetic
- **Online Booking Form** — Service selection, date & time picker, client details
- **SQLite Database** — Stores all bookings and contact enquiries persistently
- **Email Notifications** — Auto email to studio on new booking + confirmation to client
- **WhatsApp Alerts** — Instant WhatsApp to admin via Twilio on every booking
- **Admin Panel** — Password protected dashboard to view, confirm, cancel & delete bookings
- **Auto Client Notification** — WhatsApp sent to client when booking is confirmed by admin
- **Responsive Design** — Works across desktop and mobile

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Email | SMTP via Gmail |
| WhatsApp | Twilio API |
| Deployment | Railway / Render |

---

## 📁 Project Structure
```
neha-ahluwalia-studio/
├── public/
│   ├── index.html        ← Main website
│   └── admin.html        ← Admin panel
├── backend/
│   └── app.py            ← Flask server, API routes, DB logic
├── data/
│   └── .gitkeep          ← SQLite DB auto-created here on first run
├── requirements.txt
├── Procfile              ← For Railway/Render deployment
└── README.md
```

---

## 🚀 Run Locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Start the server**
```bash
cd backend
python app.py
```

**3. Open in browser**
```
Website  →  http://localhost:5000
Admin    →  http://localhost:5000/admin.html
Password →  admin@neha2026
```

---

## ⚙️ Configuration

Open `backend/app.py` and fill in the `CONFIG` block:
```python
CONFIG = {
    "smtp_user":    "your@gmail.com",       # Gmail for sending emails
    "smtp_pass":    "your_app_password",    # Gmail App Password
    "twilio_sid":   "your_twilio_sid",      # Twilio Account SID
    "twilio_token": "your_twilio_token",    # Twilio Auth Token
    "twilio_from":  "whatsapp:+14155238886" # Twilio WhatsApp number
}
```

---

## ☁️ Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo
4. Add environment variables from CONFIG
5. Railway auto-detects Python and gives you a live URL

---

## 📸 About the Client

**Neha Ahluwalia** is a verified makeup artist and beauty influencer serving Kurukshetra, Karnal and Chandigarh — with 36K+ Instagram followers and 10+ years of bridal artistry experience.

Instagram: [@nehaahluwaliaartistry](https://instagram.com/nehaahluwaliaartistry)

---

## 📄 License

This project is built as a client demo. All design and code is original.
