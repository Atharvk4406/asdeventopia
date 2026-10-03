from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot import get_bot_response
from ml_chatbot import predict_intent
import os
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
import smtplib
import uuid
import qrcode
from io import BytesIO
import base64
import pandas as pd
import threading
import time
from datetime import datetime, timedelta
import re
import socket

# ==========================
# PUBLIC URL (set by ngrok on startup)
# Falls back to local IP if ngrok is not configured
# ==========================
PUBLIC_BASE_URL = None  # Will be set by start_ngrok_tunnel()

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==========================
# DATABASE CONFIG
# ==========================
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Atharv",
    "database": "eventhopia"
}

def get_db_coonection():
    return mysql.connector.connect(**db_config)

def log_user_activity(username, action_type, details=""):
    try:
        conn = get_db_coonection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_activity_log (username, action_type, action_details) VALUES (%s, %s, %s)",
                       (username, action_type, details))
        conn.commit()
    except Exception as e:
        print("Failed to log activity:", e)
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# ==========================
# START PAGE
# ==========================
@app.route("/")
def start():
    return redirect(url_for("login"))

# ==========================
# HEALTH & INFO ENDPOINTS
# ==========================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "AI Event Management System"
    })

@app.route("/api/info")
def info():
    return jsonify({
        "service": "AI Event Management System",
        "version": "1.0.0",
        "devops_stack": ["Docker", "Jenkins", "Ansible", "Terraform", "Jira", "PyTest"]
    })


# ==========================
# HOME
# ==========================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    # Get the next upcoming event (closest future date), or fall back to most recent past event
    cursor.execute("SELECT * FROM events WHERE event_date >= CURDATE() ORDER BY event_date ASC LIMIT 1")
    latest_event = cursor.fetchone()
    if not latest_event:
        cursor.execute("SELECT * FROM events ORDER BY event_date DESC LIMIT 1")
        latest_event = cursor.fetchone()
    
    cursor.execute("SELECT * FROM events WHERE tech_fest_id IS NULL ORDER BY event_date DESC LIMIT 5")
    events = cursor.fetchall()
    
    cursor.execute("SELECT * FROM competitions")
    competitions = cursor.fetchall()
    
    cursor.execute("SELECT * FROM tech_fests WHERE show_on_home = TRUE")
    tech_fests = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM events")
    stats_events_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) as cnt FROM registrations_new")
    stats_users_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT message FROM event_feedback")
    feedbacks = cursor.fetchall()
    
    total_rating = 0
    valid_reviews = 0
    import re
    for f in feedbacks:
        msg = f['message']
        if msg:
            match = re.search(r'Overall Rating:\s*(\d+(\.\d+)?)/5', msg)
            if match:
                total_rating += float(match.group(1))
                valid_reviews += 1
                
    stats_avg_rating = round(total_rating / valid_reviews, 1) if valid_reviews > 0 else 0.0
    
    cursor.close()
    conn.close()
    
    return render_template("index.html", 
        username=session["user"], 
        latest_event=latest_event, 
        events=events, 
        competitions=competitions, 
        tech_fests=tech_fests,
        stats_events_count=stats_events_count,
        stats_users_count=stats_users_count,
        stats_avg_rating=stats_avg_rating)

# ==========================
# USER PROFILE
# ==========================
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
        
    username = session["user"]
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    import urllib.parse
    cursor.execute("SELECT COUNT(*) as cnt FROM registrations_new WHERE name = %s", (username,))
    reg_cnt = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM event_feedback WHERE username = %s", (username,))
    fb_cnt = cursor.fetchone()['cnt']
    
    points = (reg_cnt * 10) + (fb_cnt * 20)
    if points >= 100:
        badge = "👑 Campus Legend"
    elif points >= 30:
        badge = "🔥 Event Enthusiast"
    else:
        badge = "🌱 Explorer"
        
    cursor.execute("""
        SELECT u.username, 
               (COALESCE(r.reg_cnt, 0) * 10) + (COALESCE(f.fb_cnt, 0) * 20) as pts
        FROM users u
        LEFT JOIN (SELECT name, COUNT(*) as reg_cnt FROM registrations_new GROUP BY name) r ON u.username = r.name
        LEFT JOIN (SELECT username, COUNT(*) as fb_cnt FROM event_feedback GROUP BY username) f ON u.username = f.username
        ORDER BY pts DESC
    """)
    all_users = cursor.fetchall()
    user_rank = 1
    for i, u in enumerate(all_users):
        if u['username'] == username:
            user_rank = i + 1
            break

    cursor.execute("""
        SELECT r.id as reg_id, r.name as registrant, r.ticket_id, r.status, r.payment_status, r.transaction_id, e.name as event_name, e.description, e.event_date, e.venue, e.price, c.category_name 
        FROM registrations_new r
        JOIN events e ON r.event_id = e.id
        JOIN event_categories c ON r.category_id = c.id
        WHERE r.account_username = %s OR r.name = %s
    """, (username, username))
    registrations = cursor.fetchall()
    
    cursor.execute("SELECT id, name, event_date, event_time, venue, description FROM events")
    all_events = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("profile.html", username=username, registrations=registrations, points=points, badge=badge, user_rank=user_rank, all_events=all_events)

# ==========================
# FEEDBACK & NOTIFICATIONS
# ==========================
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user" not in session:
        return redirect(url_for("login"))
        
    username = session["user"]
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all events the user is registered for
    cursor.execute("""
        SELECT e.id, e.name, e.event_date 
        FROM events e
        JOIN registrations_new r ON e.id = r.event_id
        WHERE r.account_username = %s OR r.name = %s
    """, (username, username))
    attended_events = cursor.fetchall()
    
    if request.method == "POST":
        event_id = request.form.get("event_id")
        
        # Combine 8 feedback questions into single message block
        overall_rating = request.form.get("overall_rating", "")
        org_rating = request.form.get("org_rating", "")
        content_rating = request.form.get("content_rating", "")
        venue_rating = request.form.get("venue_rating", "")
        recommend = request.form.get("recommend", "")
        liked_most = request.form.get("liked_most", "")
        improvements = request.form.get("improvements", "")
        suggestions = request.form.get("suggestions", "")
        
        message = f"1. Overall Rating: {overall_rating}/5\n" \
                  f"2. Organization: {org_rating}/5\n" \
                  f"3. Content Quality: {content_rating}/5\n" \
                  f"4. Venue: {venue_rating}/5\n" \
                  f"5. Recommend: {recommend}\n" \
                  f"6. Liked Most: {liked_most}\n" \
                  f"7. Enhancements: {improvements}\n" \
                  f"8. Suggestions: {suggestions}"
        
        if event_id:
            cursor.execute("INSERT INTO event_feedback (event_id, username, message) VALUES (%s, %s, %s)", (event_id, username, message))
            conn.commit()
            
            try:
                cursor.execute("SELECT name FROM events WHERE id=%s", (event_id,))
                ev_name = cursor.fetchone()
                log_user_activity(username, "FEEDBACK_SUBMISSION", f"Submitted feedback for event '{ev_name['name'] if ev_name else event_id}'. Overall Rating: {overall_rating}/5")
            except Exception: pass

            # Send automated Thank You Email
            cursor.execute("SELECT email FROM registrations_new WHERE event_id=%s AND name=%s LIMIT 1", (event_id, username))
            user_data = cursor.fetchone()
            
            cursor.execute("SELECT name FROM events WHERE id=%s", (event_id,))
            event_data = cursor.fetchone()
            
            if user_data and event_data:
                try:
                    from email.mime.text import MIMEText
                    import smtplib

                    
                    email = user_data["email"]
                    event_name = event_data["name"]
                    
                    msg_body = f"Hi {username},\n\nThank you so much for attending '{event_name}' and leaving your valuable feedback!\n\nWe appreciate your input and hope to see you at future events.\n\nBest Regards,\nEventopia Team"
                    msg = MIMEText(msg_body)
                    msg["Subject"] = "Thank You for Your Feedback!"
                    msg["From"] = "atharvkudtarkar4406@gmail.com"
                    msg["To"] = email
                    
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
                    server.send_message(msg)
                    server.quit()
                except Exception as e:
                    print("Feedback email failed:", e)
            
        cursor.close()
        conn.close()
        return render_template("feedback.html", success=True, attended_events=attended_events)

    cursor.close()
    conn.close()
    return render_template("feedback.html", success=False, attended_events=attended_events)

@app.route("/notifications")
def notifications():
    username = session.get("user")
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notifications WHERE username = %s OR username IS NULL ORDER BY id DESC", (username,))
    notifs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("notifications.html", notifications=notifs)

# ==========================
# API NOTIFICATIONS (AI/TOAST)
# ==========================
@app.route("/api/add_notification", methods=["POST"])
def api_add_notification():
    data = request.get_json()
    if data and "title" in data and "message" in data:
        username = data.get("username", None)
        conn = get_db_coonection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (data["title"], data["message"], username))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route("/api/latest_notification", methods=["GET"])
def api_latest_notification():
    username = session.get("user")
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notifications WHERE username = %s OR username IS NULL ORDER BY id DESC LIMIT 1", (username,))
    notif = cursor.fetchone()
    cursor.close()
    conn.close()
    if notif:
        return jsonify({"id": notif["id"], "title": notif["title"], "message": notif["message"]})
    return jsonify({})

@app.route("/api/unread_notifications_count", methods=["GET"])
def api_unread_notifications_count():
    username = session.get("user")
    if not username:
        return jsonify({"count": 0})
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE username=%s OR username IS NULL", (username,))
    notif = cursor.fetchone()
    cursor.close()
    conn.close()
    
    count = notif["count"] if notif else 0
    return jsonify({"count": count})

# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_coonection()
        cursor = conn.cursor(buffered=True)

        cursor.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):

            session.clear()
            session["user"] = user[1]

            # -------------------------
            # ADD TO ACTIVE USERS
            # -------------------------
            cursor.execute("SELECT * FROM active_users WHERE username=%s", (user[1],))
            existing = cursor.fetchone()

            if not existing:
                cursor.execute("INSERT INTO active_users (username) VALUES (%s)", (user[1],))
            else:
                cursor.execute("UPDATE active_users SET login_time=CURRENT_TIMESTAMP WHERE username=%s", (user[1],))
            
            conn.commit()

            cursor.close()
            conn.close()

            try:
                log_user_activity(user[1], "LOGIN", "User logged into the system.")
            except Exception: pass

            return redirect(url_for("home"))

        cursor.close()
        conn.close()

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# ==========================
# REGISTER
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        email = request.form["email"]
        user_class = request.form["class"]
        phone = request.form.get("phone")

        # --- VALIDATION ---
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_regex = r'^\d{10}$'

        if not re.match(email_regex, email):
            return render_template("register.html", error="Invalid email format")
        
        if phone and not re.match(phone_regex, phone):
            return render_template("register.html", error="Mobile number must be exactly 10 digits")

        try:
            conn = get_db_coonection()
            cursor = conn.cursor(buffered=True) # Stability fix

            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template("register.html", error="Username already exists")

            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template("register.html", error="Email already used")

            # Note: Storing phone as plain text for accessibility. 
            # If "Hashing" was strictly required, one-way hash would break display features.
            cursor.execute(
                "INSERT INTO users (username, password, email, class, phone) VALUES (%s, %s, %s, %s, %s)",
                (username, password, email, user_class, phone)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("login"))

        except mysql.connector.Error as e:
            return render_template("register.html", error="Database error occurred.")

    return render_template("register.html")

# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():

    username = session.get("user")

    conn = get_db_coonection()
    cursor = conn.cursor(buffered=True)

    cursor.execute("DELETE FROM active_users WHERE username=%s", (username,))
    conn.commit()

    cursor.close()
    conn.close()

    session.clear()

    return redirect(url_for("login"))

# ==========================
# CHATBOT
# ==========================
@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    try:
        data = request.get_json()
        message = data.get("message","")
        
        try:
            username = session.get("user", "Anonymous")
            if message.strip():
                log_user_activity(username, "ASK_AI", f"Asked: {message}")
        except Exception: pass

        response = get_bot_response(message, db_config)

        return response

    except Exception as e:
        print("AI ERROR:", e)
        return jsonify({"response": "AI assistant error"})

# ==========================
# EVENTS PAGE
# ==========================
@app.route("/events")
def events_page():
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events WHERE tech_fest_id IS NULL")
    events = cursor.fetchall()
    
    cursor.execute("SELECT * FROM competitions")
    competitions = cursor.fetchall()

    cursor.execute("SELECT * FROM tech_fests")
    tech_fests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("events.html", events=events, competitions=competitions, tech_fests=tech_fests)

# ==========================
# TECH FEST DETAILS
# ==========================
@app.route("/techfest/<int:id>")
def techfest_details(id):
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tech_fests WHERE id=%s", (id,))
    techfest = cursor.fetchone()
    
    if not techfest:
        cursor.close()
        conn.close()
        return redirect("/events")
        
    cursor.execute("SELECT * FROM events WHERE tech_fest_id=%s", (id,))
    events = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("techfest.html", techfest=techfest, events=events)

# ==========================
# EVENT CATEGORIES
# ==========================
@app.route("/event_categories/<int:event_id>")
def event_categories(event_id):

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM event_categories WHERE event_id=%s",(event_id,))
    categories = cursor.fetchall()

    if not categories:
        cursor.execute("INSERT INTO event_categories (event_id, category_name) VALUES (%s, %s)", (event_id, "General Registration"))
        conn.commit()
        cursor.execute("SELECT * FROM event_categories WHERE event_id=%s",(event_id,))
        categories = cursor.fetchall()

    cursor.execute("SELECT * FROM events WHERE id=%s",(event_id,))
    event = cursor.fetchone()

    cursor.execute("SELECT * FROM events WHERE image IS NOT NULL AND id != %s ORDER BY event_date DESC LIMIT 3", (event_id,))
    past_events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("event_details.html",categories=categories,event=event, past_events=past_events)

def get_local_ip():
    """Fallback: get LAN IP when ngrok is not running."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def _read_ngrok_url_from_api():
    """Read the active ngrok tunnel URL from ngrok's local API (port 4040)."""
    try:
        import urllib.request, json
        with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as resp:
            data = json.loads(resp.read())
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                url = t.get("public_url", "")
                if url.startswith("https://"):
                    return url
            for t in tunnels:
                url = t.get("public_url", "")
                if url.startswith("http://"):
                    return url.replace("http://", "https://")
    except Exception:
        pass
    return None

def get_base_url():
    """Returns the live ngrok URL from ngrok's API, falls back to local IP."""
    global PUBLIC_BASE_URL
    # Always try to read the live URL from ngrok's local API first
    live_url = _read_ngrok_url_from_api()
    if live_url:
        PUBLIC_BASE_URL = live_url
        return live_url
    # If ngrok is not running at all, fallback to local IP
    return f"http://{get_local_ip()}:5000"

def generate_ticket_qr(ticket_id, name="", event_name="", category_name="", event_date="", event_time="", venue="", class_name="", team_name=""):
    os.makedirs("static/tickets", exist_ok=True)
    base_url = get_base_url()
    ticket_url = f"{base_url}/verify/{ticket_id}"
    # Encode only the URL — any phone camera opens it directly
    qr = qrcode.QRCode(version=None, box_size=10, border=4)
    qr.add_data(ticket_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filepath = f"static/tickets/{ticket_id}.png"
    img.save(filepath)
    return filepath

# ==========================
# NGROK TUNNEL AUTO-START
# Flask no longer manages the ngrok process directly.
# Instead, ngrok runs as a SEPARATE PERSISTENT process.
# Flask just reads the URL from ngrok's local API (port 4040).
# ==========================
def start_ngrok_tunnel():
    """
    Launch ngrok as a completely independent subprocess and monitor it.
    This is the most reliable approach — ngrok runs separately from Flask so 
    Flask reloads/crashes do NOT kill the tunnel.
    """
    global PUBLIC_BASE_URL
    ngrok_token = os.getenv("NGROK_AUTHTOKEN", "")
    if not ngrok_token:
        print("[ngrok] No NGROK_AUTHTOKEN in .env — using local IP for QR codes.")
        return

    domain = os.getenv("NGROK_DOMAIN", "endpoint-bright-retiring.ngrok-free.dev").strip()

    def _launch_ngrok():
        """Kill any existing ngrok processes and launch a fresh one."""
        import subprocess, platform
        # Kill old ngrok processes
        if platform.system() == "Windows":
            os.system("taskkill /F /IM ngrok.exe >nul 2>&1")
        else:
            os.system("pkill -f ngrok >/dev/null 2>&1")
        time.sleep(2)

        # Build the command - modern ngrok uses --url for custom domains
        if domain:
            cmd = ["ngrok", "http", "5000", "--authtoken", ngrok_token, "--url", f"https://{domain}", "--log", "false"]
        else:
            cmd = ["ngrok", "http", "5000", "--authtoken", ngrok_token, "--log", "false"]

        try:
            # Launch ngrok as a fully detached process so it survives Flask restarts
            if platform.system() == "Windows":
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
            else:
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            print(f"[ngrok] Launched ngrok subprocess for domain: {domain or 'auto'}")
        except FileNotFoundError:
            # ngrok not in PATH - try pyngrok as fallback
            try:
                from pyngrok import ngrok as pyngrok, conf as pyngrok_conf
                pyngrok_conf.get_default().auth_token = ngrok_token
                if domain:
                    tunnel = pyngrok.connect(5000, "http", domain=domain)
                else:
                    tunnel = pyngrok.connect(5000, "http")
                print(f"[ngrok] pyngrok fallback tunnel: {tunnel.public_url}")
            except Exception as pe:
                print("[ngrok] pyngrok fallback also failed:", pe)

    def _regen_all_qrs(base_url):
        """Regenerate all ticket QR codes with the new public URL."""
        try:
            conn = get_db_coonection()
            c = conn.cursor(dictionary=True)
            c.execute("SELECT ticket_id FROM registrations_new WHERE ticket_id IS NOT NULL")
            rows = c.fetchall()
            c.close()
            conn.close()
            count = 0
            for row in rows:
                try:
                    tid = row['ticket_id']
                    url = f"{base_url}/verify/{tid}"
                    qr_img = qrcode.QRCode(version=None, box_size=10, border=4)
                    qr_img.add_data(url)
                    qr_img.make(fit=True)
                    img = qr_img.make_image(fill_color="black", back_color="white")
                    os.makedirs("static/tickets", exist_ok=True)
                    img.save(f"static/tickets/{tid}.png")
                    count += 1
                except Exception:
                    pass
            print(f"[ngrok] Regenerated {count} QR code(s) with public URL: {base_url}")
        except Exception as e:
            print("[ngrok] QR regen error:", e)

    # Launch ngrok immediately on startup
    _launch_ngrok()

    # Wait for ngrok's local API to become available (up to 10 seconds)
    print("[ngrok] Waiting for tunnel to come online...")
    for _ in range(20):
        url = _read_ngrok_url_from_api()
        if url:
            PUBLIC_BASE_URL = url
            print(f"[ngrok] Tunnel active: {PUBLIC_BASE_URL}")
            _regen_all_qrs(PUBLIC_BASE_URL)
            break
        time.sleep(0.5)
    else:
        print(f"[ngrok] Tunnel did not start in time. Falling back to local IP.")

    # Monitor loop — checks every 15 seconds if ngrok is still alive
    while True:
        time.sleep(15)
        url = _read_ngrok_url_from_api()
        if url:
            PUBLIC_BASE_URL = url  # Keep it updated
        else:
            print("[ngrok] Tunnel appears to be down — restarting...")
            PUBLIC_BASE_URL = None
            _launch_ngrok()
            # Wait for new tunnel to come up
            for _ in range(20):
                url = _read_ngrok_url_from_api()
                if url:
                    PUBLIC_BASE_URL = url
                    print(f"[ngrok] Tunnel restored: {PUBLIC_BASE_URL}")
                    _regen_all_qrs(PUBLIC_BASE_URL)
                    break
                time.sleep(0.5)


def finalize_registration(category, event, names, emails, phones, team_name, transaction_id=None, branches=None, classes=None, account_username=None):
    from flask import render_template
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    leader_name = names[0]
    leader_email = emails[0]
    leader_phone = phones[0]
    ticket_ids = []

    for i in range(len(names)):
        ticket_id = uuid.uuid4().hex[:12].upper()
        ticket_ids.append(ticket_id)
        
        branch_val = branches[i] if branches and i < len(branches) else None
        class_val  = classes[i]  if classes  and i < len(classes)  else None
        
        generate_ticket_qr(
            ticket_id,
            name=names[i],
            event_name=event.get('name', ''),
            category_name=category.get('category_name', ''),
            event_date=str(event.get('event_date', '')),
            event_time=str(event.get('event_time', '')),
            venue=event.get('venue', ''),
            class_name=class_val or '',
            team_name=team_name or ''
        )

        status = 'Registered'
        payment_status = 'Completed' if transaction_id or not event.get('price') else 'Pending'
        branch_val = branches[i] if branches and i < len(branches) else None
        class_val  = classes[i]  if classes  and i < len(classes)  else None

        cursor.execute("""
        INSERT INTO registrations_new(event_id,category_id,name,email,phone,branch,class,team_name,ticket_id,status,payment_status,transaction_id,account_username)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,(category["event_id"],category['id'],names[i],emails[i],phones[i],branch_val,class_val,team_name,ticket_id,status,payment_status,transaction_id,account_username))

        try:
            log_user_activity(names[i], "EVENT_REGISTRATION", f"Registered for '{event['name']}' in category '{category['category_name']}'. Ticket: {ticket_id}")
        except Exception: pass

    conn.commit()

    # APP NOTIFICATION (Initially generic, will be updated by AI in background)
    notification_title = "New Event Registration ⭐"
    notification_message = f"{leader_name} just registered for {event['name']} ({category['category_name']})!"
    if team_name:
         notification_message = f"Team '{team_name}' just registered for {event['name']} ({category['category_name']})!"
    
    notif_id = None
    try:
        # Send notification to the logged-in user account if available, otherwise fallback to leader_name
        target_user = account_username if account_username else leader_name
        cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notification_title, notification_message, target_user))
        conn.commit()
        notif_id = cursor.lastrowid
    except Exception as e:
        print("Notification insert failed:", e)

    cursor.close()
    conn.close()

    # -------------------------------------------------------
    # Send email + SMS in background so the page loads fast
    # -------------------------------------------------------
    _ticket_ids    = list(ticket_ids)
    _names         = list(names)
    _emails        = list(emails)
    _phones        = list(phones)
    _event         = dict(event)
    _category      = dict(category)
    _team_name     = team_name
    _transaction_id = transaction_id
    _leader_name   = leader_name
    _leader_email  = leader_email
    _leader_phone  = leader_phone
    _notif_id      = notif_id
    _notif_msg     = notification_message

    def _send_bg():
        nonlocal _notif_msg
        # 1. AI Message Update (Background)
        if _notif_id:
            try:
                from chatbot import model
                if model:
                    prompt_name = _team_name if _team_name else _leader_name
                    prompt = f"Write a vibrant, hyped 1-sentence announcement for a college portal that a student/team named '{prompt_name}' just registered for '{_event['name']}' (module: '{_category['category_name']}'). Use emojis. No quotes."
                    response = model.generate_content(prompt)
                    if response and response.text:
                        cleaned_ai_msg = response.text.replace('"', '').replace("'", '').strip()
                        if cleaned_ai_msg != "":
                            conn_bg = get_db_coonection()
                            cursor_bg = conn_bg.cursor()
                            cursor_bg.execute("UPDATE notifications SET message=%s WHERE id=%s", (cleaned_ai_msg, _notif_id))
                            conn_bg.commit()
                            cursor_bg.close()
                            conn_bg.close()
                            _notif_msg = cleaned_ai_msg
            except Exception as e:
                print("AI notification update failed:", e)

        # 2. SMS
        try:
            from twilio.rest import Client
            twilio_sid   = os.getenv("TWILIO_ACCOUNT_SID")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
            twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
            if twilio_sid and twilio_token and twilio_phone:
                client = Client(twilio_sid, twilio_token)
                sms_body = f"Eventopia Quick Update: {_notif_msg}"
                formatted_phone = _leader_phone if _leader_phone.startswith('+') else f"+91{_leader_phone}"
                client.messages.create(body=sms_body, from_=twilio_phone, to=formatted_phone)
        except Exception as e:
            print("SMS sending failed:", e)

        # EMAIL with QR ticket attachments
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.image import MIMEImage
            import smtplib
            teammates_text = "\n".join([
                f"- {_names[i]} ({_emails[i]}) [Ticket ID: {_ticket_ids[i]}]"
                for i in range(len(_names))
            ])
            body = (
                f"Congratulations {_leader_name}!\n\n"
                f"Your registration is confirmed. Show your QR code / Ticket ID at the venue.\n\n"
                f"Event    : {_event['name']}\n"
                f"Category : {_category['category_name']}\n"
                + (f"Team Name: {_team_name}\n" if _team_name else "") +
                f"Venue    : {_event['venue']}\n"
                f"Date     : {_event['event_date']}\n"
                f"Time     : {_event['event_time']}\n"
                f"Txn ID   : {_transaction_id if _transaction_id else 'N/A (Free/Pending)'}\n\n"
                f"Registered Members & Tickets:\n{teammates_text}\n\n"
                f"We look forward to seeing you there!\n\nEventopia Team"
            )
            msg = MIMEMultipart()
            msg["Subject"] = "Event Registration Confirmed (Tickets Inside!)"
            msg["From"]    = "atharvkudtarkar4406@gmail.com"
            msg["To"]      = _leader_email
            msg.attach(MIMEText(body, 'plain'))
            for t_id in _ticket_ids:
                try:
                    with open(f"static/tickets/{t_id}.png", 'rb') as f:
                        img_data = f.read()
                    image = MIMEImage(img_data, name=f"{t_id}.png")
                    msg.attach(image)
                except Exception as e:
                    print("Failed to attach ticket image:", e)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("Email sending failed:", e)

    bg_thread = threading.Thread(target=_send_bg, daemon=True)
    bg_thread.start()

    return render_template(
        "registration_success.html",
        event=_event,
        category=_category,
        name=_leader_name
    )

@app.route("/register/<int:category_id>", methods=["GET","POST"])
def register_event(category_id):
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM event_categories WHERE id=%s",(category_id,))
    category = cursor.fetchone()

    cursor.execute("SELECT * FROM events WHERE id=%s",(category["event_id"],))
    event = cursor.fetchone()

    # --- Block registrations: check registration_deadline first, then event_date ---
    now = datetime.now()
    reg_deadline = event.get('registration_deadline')
    event_date_val = event.get('event_date')
    is_closed = False
    closed_reason = ""

    if reg_deadline:
        # Admin has set an explicit deadline
        try:
            if isinstance(reg_deadline, str):
                deadline_dt = datetime.strptime(reg_deadline, '%Y-%m-%d %H:%M:%S')
            else:
                deadline_dt = reg_deadline  # already datetime from MySQL
            if now > deadline_dt:
                is_closed = True
                closed_reason = (
                    f"Registration for this event closed on "
                    f"<strong>{deadline_dt.strftime('%d %b %Y at %I:%M %p')}</strong>. "
                    f"Contact the admin if you still wish to participate."
                )
        except Exception:
            pass
    elif event_date_val:
        # No explicit deadline — use event date
        try:
            if isinstance(event_date_val, str):
                event_date_obj = datetime.strptime(event_date_val, '%Y-%m-%d').date()
            else:
                event_date_obj = event_date_val
            if event_date_obj < now.date():
                is_closed = True
                closed_reason = (
                    f"This event was held on <strong>{event_date_obj.strftime('%d %b %Y')}</strong>, "
                    f"which has already passed. Registrations are no longer accepted."
                )
        except Exception:
            pass

    if is_closed:
        cursor.close()
        conn.close()
        return render_template("registration.html", category=category, event=event,
                               error=closed_reason,
                               registration_closed=True)

    if request.method == "POST":
        names     = request.form.getlist("name[]")
        emails    = request.form.getlist("email[]")
        phones    = request.form.getlist("phone[]")
        branches  = request.form.getlist("branch[]")
        classes   = request.form.getlist("class[]")
        team_name = request.form.get("team_name") if request.form.get("team_name") else None

        # --- SERVER-SIDE VALIDATION ---
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_regex = r'^\d{10}$'

        # --- RULE 1: Full name required (at least first + last name) ---
        for i in range(len(names)):
            name_parts = names[i].strip().split()
            if len(name_parts) < 2:
                return render_template("registration.html", category=category, event=event,
                                       error=f"Full name required for member {i+1}. Please enter first name AND last name (e.g. 'Atharv Kudtarkar').")

        # --- RULE 2: Email must match logged-in user's email ---
        logged_in_user = session.get("user")
        if logged_in_user:
            conn2 = get_db_coonection()
            cur2 = conn2.cursor(dictionary=True)
            cur2.execute("SELECT email FROM users WHERE username=%s", (logged_in_user,))
            user_row = cur2.fetchone()
            cur2.close()
            conn2.close()

            if user_row:
                logged_in_email = user_row['email'].strip().lower()
                # The first member's email (leader) MUST be the logged-in user's email
                if emails[0].strip().lower() != logged_in_email:
                    return render_template("registration.html", category=category, event=event,
                                           error=f"You must register with your own email ({user_row['email']}). You cannot use a different email while logged into this account.")

        for i in range(len(emails)):
            curr_email = emails[i].strip()
            curr_phone = phones[i].strip() if i < len(phones) else ""

            if not re.match(email_regex, curr_email):
                return render_template("registration.html", category=category, event=event, 
                                       error=f"Invalid email format for member {i+1} ({names[i] if i < len(names) else 'Unknown'}): '{curr_email}'")
            
            if not re.match(phone_regex, curr_phone):
                return render_template("registration.html", category=category, event=event, 
                                       error=f"Phone number for member {i+1} ({names[i] if i < len(names) else 'Unknown'}) must be exactly 10 digits. Found: '{curr_phone}'")

        # --- RULE 3: Allow multiple registrations with same email (User Requested) ---
        # Note: We previously blocked this, but now allow it for flexibility.
        pass

        price = event.get('price')
        if price and int(price) > 0:
            # Save to session and redirect to checkout
            session['checkout_data'] = {
                'category': category,
                'event': event,
                'names': names,
                'emails': emails,
                'phones': phones,
                'branches': branches,
                'classes': classes,
                'team_name': team_name,
                'amount': int(price) * len(names)
            }
            cursor.close()
            conn.close()
            return redirect(url_for('checkout'))
        else:
            # Free registration
            res = finalize_registration(category, event, names, emails, phones, team_name,
                                        branches=branches, classes=classes, account_username=session.get('user'))
            cursor.close()
            conn.close()
            return res

    cursor.close()
    conn.close()
    return render_template("registration.html",category=category, event=event)

@app.route("/checkout")
def checkout():
    if 'checkout_data' not in session:
        return redirect('/events')
        
    data = session['checkout_data']
    amount = data['amount']
    # Create UPI Intent string (generic example)
    upi_id = "eventopia@okhdfcbank"
    merchant_name = "Eventopia"
    upi_url = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&cu=INR"
    
    # Generate QR Code dynamically
    qr = qrcode.QRCode(version=1, box_size=5, border=3)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return render_template("checkout.html", amount=amount, event_name=data['event']['name'], upi_url=upi_url, qr_code_data=qr_code_b64)

@app.route("/process_payment", methods=["POST"])
def process_payment():
    if 'checkout_data' not in session:
        return redirect('/events')
        
    transaction_id = request.form.get('transaction_id')
    data = session['checkout_data']
    
    res = finalize_registration(
        data['category'], 
        data['event'], 
        data['names'], 
        data['emails'], 
        data['phones'], 
        data['team_name'], 
        transaction_id,
        branches=data.get('branches'),
        classes=data.get('classes'),
        account_username=session.get('user')
    )
    
    session.pop('checkout_data', None)
    return res


@app.route("/add_category", methods=["POST"])
def add_category():
    if "admin" not in session:
        return redirect("/admin_login")

    event_id = request.form["event_id"]
    category_name = request.form["category_name"]

    conn = get_db_coonection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO event_categories(event_id,category_name) VALUES(%s,%s)",
        (event_id,category_name)
    )

    try:
        cursor.execute("SELECT name FROM events WHERE id=%s", (event_id,))
        event = cursor.fetchone()
        event_name = event[0] if event else "an event"
        cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", ("New Category Added ✨", f"A new category '{category_name}' was added to {event_name}!"))
    except Exception as e:
        print("Category notice error:", e)

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin")
@app.route("/delete_event/<int:id>")
def delete_event(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor()

    # get registered users to notify them before deleting
    cursor.execute("SELECT name, email FROM registrations_new WHERE event_id=%s", (id,))
    registered_users = cursor.fetchall()
    
    cursor.execute("SELECT name FROM events WHERE id=%s", (id,))
    event_info = cursor.fetchone()
    event_name = event_info[0] if event_info else "An event"

    if registered_users:
        notification_title = "Event Cancelled 🚫"
        notification_message = f"The event '{event_name}' has been cancelled. Your registration is removed."
        
        # Insert DB Notifications first so they don't fail if SMTP fails
        for user in registered_users:
            try:
                cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notification_title, notification_message, user[0]))
            except Exception as e:
                print("Failed to insert db notification for user:", e)
        conn.commit()

        # Then attempt to email
        try:
            from email.mime.text import MIMEText
            import smtplib
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
            for user in registered_users:
                if user[1]:
                    try:
                        msg = MIMEText(f"Hello {user[0]},\n\nThe event '{event_name}' has been cancelled. Your registration has been removed.\n\nBest,\nEventopia Team")
                        msg["Subject"] = f"Event Cancelled: {event_name}"
                        msg["From"] = "atharvkudtarkar4406@gmail.com"
                        msg["To"] = user[1]
                        server.send_message(msg)
                    except Exception as e:
                        print("Failed to email user of event deletion:", e)
            server.quit()
        except Exception as e:
            print("Failed to setup deletion email:", e)

    # delete registrations first
    cursor.execute("""
    DELETE FROM registrations_new 
    WHERE event_id=%s
    """,(id,))

    # delete categories
    cursor.execute("""
    DELETE FROM event_categories 
    WHERE event_id=%s
    """,(id,))

    # delete event
    cursor.execute("""
    DELETE FROM events 
    WHERE id=%s
    """,(id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin")

@app.route("/delete_user/<int:id>")
def delete_user(id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    reason = request.args.get("reason", "No reason provided.")

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user details for sending email
    cursor.execute("SELECT r.name, r.email, e.name as event_name FROM registrations_new r JOIN events e ON r.event_id = e.id WHERE r.id=%s", (id,))
    reg = cursor.fetchone()

    cursor.execute("DELETE FROM registrations_new WHERE id=%s",(id,))
    conn.commit()
    
    if reg:
        # Send App Notification
        try:
            notification_title = "Registration Cancelled ❌"
            notification_message = f"Your registration for '{reg['event_name']}' has been cancelled by the administrator. Reason: {reason}"
            cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notification_title, notification_message, reg['name']))
            conn.commit()
        except Exception as e:
            print("Failed to add cancellation app notification:", e)

        # Send Email notification explaining the reason
        try:
            from email.mime.text import MIMEText
            import smtplib

            
            msg = MIMEText(f"Hello {reg['name']},\n\nYour registration for the event '{reg['event_name']}' has been cancelled by the administrator.\n\nReason: {reason}\n\nBest Regards,\nEventopia Team")
            msg["Subject"] = "Registration Cancelled"
            msg["From"] = "atharvkudtarkar4406@gmail.com"
            msg["To"] = reg["email"]
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("Failed to send cancellation email:", e)

    cursor.close()
    conn.close()

    return redirect("/admin")

@app.route("/cancel_registration/<int:id>", methods=["POST"])
def cancel_registration(id):
    if "user" not in session:
        return redirect(url_for("login"))
        
    username = session["user"]
    
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify the registration belongs to this user
    cursor.execute("SELECT r.name, r.email, e.name as event_name FROM registrations_new r JOIN events e ON r.event_id = e.id WHERE r.id=%s AND r.account_username=%s", (id, username))
    reg = cursor.fetchone()
    
    if reg:
        cursor.execute("DELETE FROM registrations_new WHERE id=%s", (id,))
        conn.commit()
        
        try:
            log_user_activity(username, "CANCEL_REGISTRATION", f"Cancelled registration for event '{reg['event_name']}'.")
        except Exception: pass
        
        # Send confirmation email
        try:
            from email.mime.text import MIMEText
            import smtplib

            
            msg = MIMEText(f"Hello {reg['name']},\n\nYou have successfully cancelled your registration for the event '{reg['event_name']}'.\n\nWe hope to see you at future events!\n\nBest Regards,\nEventopia")
            msg["Subject"] = "Registration Cancellation Confirmed"
            msg["From"] = "atharvkudtarkar4406@gmail.com"
            msg["To"] = reg["email"]
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("Failed to send user cancellation email:", e)

    cursor.close()
    conn.close()
    
    return redirect(url_for("profile"))
@app.route('/add_event', methods=['POST'])
def add_event():
    if "admin" not in session:
        return redirect("/admin_login")

    name = request.form['name']
    description = request.form['description']
    category = request.form['category']
    event_type = request.form.get('event_type', 'Individual')
    department = request.form.get('department')
    tech_fest_id = request.form.get('tech_fest_id')
    if not tech_fest_id:
        tech_fest_id = None

    event_date = request.form['event_date']
    event_time = request.form['event_time']
    venue = request.form['venue']
    price = request.form.get('price', 0)

    registration_deadline = request.form.get('registration_deadline') or None

    image_file = request.files['image']
    filename = None

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO events 
            (name, description, category, department, tech_fest_id, event_date, event_time, venue, image, price, event_type, registration_deadline)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, description, category, department, tech_fest_id, event_date, event_time, venue, filename, price, event_type, registration_deadline))
    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        return f"Database Error: Invalid input data. Ensure correct format (e.g. valid date). Details: {err}", 400

    event_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO event_categories (event_id, category_name)
        VALUES (%s, %s)
    """, (event_id, "General Registration"))

    # Send Notification and Emails for new event
    try:
        notification_title = "New Event Added! 🎉"
        notification_message = f"Check out our new event: {name}. Don't miss out!"
        cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (notification_title, notification_message))
        
        cursor.execute("SELECT id, username, email FROM users")
        all_users = cursor.fetchall()
        from email.mime.text import MIMEText
        import smtplib
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
        for u in all_users:
            if len(u) > 2 and u[2]:  # If email exists
                msg = MIMEText(f"Hello {u[1]},\n\nA new event '{name}' has been added to our system!\n\nVenue: {venue}\nDate: {event_date}\n\nLog in to check it out.\n\nBest,\nEventopia Team")
                msg["Subject"] = f"New Event Alert: {name}"
                msg["From"] = "atharvkudtarkar4406@gmail.com"
                msg["To"] = u[2]
                server.send_message(msg)
        server.quit()
    except Exception as e:
        print("New event notification failed:", e)

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/admin') # Better redirect to admin after adding event

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Get existing event name
        cursor.execute("SELECT name FROM events WHERE id=%s", (id,))
        event_info = cursor.fetchone()
        event_name = event_info["name"] if event_info else "An Event"

        event_date = request.form['event_date']
        event_time = request.form['event_time']
        price = request.form.get('price', 0)
        category = request.form.get('category')
        event_type = request.form.get('event_type', 'Individual')
        department = request.form.get('department')
        tech_fest_id = request.form.get('tech_fest_id')
        if not tech_fest_id:
            tech_fest_id = None
        
        registration_deadline = request.form.get('registration_deadline') or None

        cursor.execute("""
            UPDATE events 
            SET event_date=%s, event_time=%s, price=%s, category=%s, department=%s, tech_fest_id=%s, event_type=%s, registration_deadline=%s
            WHERE id=%s
        """, (event_date, event_time, price, category, department, tech_fest_id, event_type, registration_deadline, id))
        
        # Add Notification for the update
        try:
            notification_title = "Event Rescheduled"
            notification_message = f"Heads up! '{event_name}' has been updated to {event_date} at {event_time}."
            cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (notification_title, notification_message))

            # If a registration deadline was set, send a deadline-specific notification
            if registration_deadline:
                deadline_notif_msg = (
                    f"Registration for '{event_name}' closes on "
                    f"{registration_deadline.replace('T', ' ')}. Register before it's too late!"
                )
                cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)",
                               ("Registration Deadline Set", deadline_notif_msg))
            
            cursor.execute("SELECT email, name FROM registrations_new WHERE event_id=%s", (id,))
            regs = cursor.fetchall()
            if regs:
                from email.mime.text import MIMEText
                import smtplib
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
                for r in regs:
                    if r.get('email'):
                        msg = MIMEText(f"Hello {r['name']},\n\nHeads up! The event '{event_name}' has been updated to {event_date} at {event_time}.\n\nBest,\nEventopia Team")
                        msg["Subject"] = f"Event Update: {event_name}"
                        msg["From"] = "atharvkudtarkar4406@gmail.com"
                        msg["To"] = r['email']
                        try:
                            server.send_message(msg)
                        except Exception as e:
                            print("Send message error:", e)
                server.quit()
        except Exception as e:
            print("Failed to add edit notification:", e)
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect("/admin")
        
    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()
    
    cursor.execute("SELECT * FROM tech_fests")
    tech_fests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not event:
        return redirect("/admin")
        
    return render_template("edit_event.html", event=event, tech_fests=tech_fests)

@app.route('/add_competition', methods=['POST'])
def add_competition():
    if "admin" not in session:
        return redirect("/admin_login")

    name = request.form['name']
    comp_type = request.form['type']
    description = request.form['description']
    comp_date = request.form['competition_date']
    venue = request.form['venue']

    image_file = request.files.get('image')
    filename = None
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO competitions 
            (name, type, description, competition_date, venue, image)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, comp_type, description, comp_date, venue, filename))
        
        try:
            cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", ("New Competition! 🏆", f"Check out the new competition: {name}"))
        except Exception:
            pass

    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        return f"Database Error: Invalid input data. Ensure correct format (e.g. valid date). Details: {err}", 400

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/admin')

@app.route('/edit_competition/<int:id>', methods=['GET', 'POST'])
def edit_competition(id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        comp_type = request.form['type']
        comp_date = request.form['competition_date']
        venue = request.form['venue']
        description = request.form['description']
        
        cursor.execute("""
            UPDATE competitions 
            SET name=%s, type=%s, description=%s, competition_date=%s, venue=%s
            WHERE id=%s
        """, (name, comp_type, description, comp_date, venue, id))
        
        try:
            notification_title = "Competition Updated ✏️"
            notification_message = f"Details for the competition '{name}' have been updated."
            cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (notification_title, notification_message))
        except Exception:
            pass
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect("/admin")
        
    cursor.execute("SELECT * FROM competitions WHERE id=%s", (id,))
    comp = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not comp:
        return redirect("/admin")
        
    return render_template("edit_competition.html", comp=comp)

@app.route('/add_tech_fest', methods=['POST'])
def add_tech_fest():
    if "admin" not in session:
        return redirect("/admin_login")

    name = request.form['name']
    department = request.form['department']
    description = request.form['description']
    fest_date = request.form['fest_date']
    venue = request.form['venue']

    show_on_home = True if request.form.get('show_on_home') else False

    image_file = request.files.get('image')
    filename = None
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO tech_fests 
            (name, department, description, fest_date, venue, image, show_on_home)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (name, department, description, fest_date, venue, filename, show_on_home))
    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        return f"Database Error: Invalid input data. Ensure correct format (e.g. valid date). Details: {err}", 400
    
    # Send Notification
    try:
        notification_title = "New Tech Fest Announced! 🚀"
        notification_message = f"The {department} department just announced {name}! Get ready for exciting sub-events."
        cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (notification_title, notification_message))
    except Exception as e:
        print("Notification failed:", e)

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/admin')

@app.route('/edit_tech_fest/<int:id>', methods=['GET', 'POST'])
def edit_tech_fest(id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        description = request.form['description']
        fest_date = request.form['fest_date']
        venue = request.form['venue']
        show_on_home = True if request.form.get('show_on_home') else False
        
        cursor.execute("""
            UPDATE tech_fests 
            SET name=%s, department=%s, description=%s, fest_date=%s, venue=%s, show_on_home=%s
            WHERE id=%s
        """, (name, department, description, fest_date, venue, show_on_home, id))
        
        # Send Notification
        try:
            notification_title = "Tech Fest Updated ✏️"
            notification_message = f"Details for {name} have been updated. Check them out!"
            cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", (notification_title, notification_message))
        except Exception as e:
            pass
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect("/admin")
        
    cursor.execute("SELECT * FROM tech_fests WHERE id=%s", (id,))
    fest = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not fest:
        return redirect("/admin")
        
    return render_template("edit_tech_fest.html", fest=fest)

@app.route('/add_sub_event/<int:tech_fest_id>', methods=['GET'])
def add_sub_event(tech_fest_id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tech_fests WHERE id=%s", (tech_fest_id,))
    fest = cursor.fetchone()
    
    cursor.execute("SELECT * FROM tech_fests")
    all_tech_fests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not fest:
        return redirect("/admin")
    
    return render_template("add_sub_event.html", fest=fest, tech_fests=all_tech_fests)

@app.route("/delete_competition/<int:id>")
def delete_competition(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM competitions WHERE id=%s", (id,))
        comp = cursor.fetchone()
        name = comp[0] if comp else "A competition"
        cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", ("Competition Cancelled 🚫", f"The competition '{name}' has been cancelled."))
    except Exception:
        pass

    cursor.execute("DELETE FROM competitions WHERE id=%s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()

    return redirect("/admin")

@app.route("/delete_tech_fest/<int:id>")
def delete_tech_fest(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM tech_fests WHERE id=%s", (id,))
        fest = cursor.fetchone()
        name = fest[0] if fest else "A tech fest"
        cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", ("Tech Fest Cancelled 🚫", f"The tech fest '{name}' has been cancelled."))
    except Exception:
        pass

    cursor.execute("DELETE FROM tech_fests WHERE id=%s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()

    return redirect("/admin")
@app.route("/delete_category/<int:id>")
def delete_category(id):
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT c.category_name, e.name FROM event_categories c JOIN events e ON c.event_id=e.id WHERE c.id=%s", (id,))
        cat = cursor.fetchone()
        if cat:
            cursor.execute("INSERT INTO notifications (title, message) VALUES (%s, %s)", ("Category Removed 🗑️", f"The category '{cat[0]}' was removed from {cat[1]}."))
    except Exception:
        pass

    cursor.execute("DELETE FROM event_categories WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin")
@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect("/admin_login")

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@gmail.com" and password == "1234":
            session.clear()
            session["admin"] = True
            return redirect("/admin")

    return render_template("admin_login.html")

@app.route("/admin/remove_system_user/<int:user_id>", methods=["POST"])
def remove_system_user(user_id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    # Get username first
    cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
    user_row = cursor.fetchone()
    
    if user_row:
        uname = user_row['username']
        # Delete dependencies
        cursor.execute("DELETE FROM active_users WHERE username=%s", (uname,))
        cursor.execute("DELETE FROM event_feedback WHERE username=%s", (uname,))
        cursor.execute("DELETE FROM notifications WHERE username=%s", (uname,))
        cursor.execute("DELETE FROM registrations_new WHERE name=%s", (uname,))
        # Finally delete account
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        
    cursor.close()
    conn.close()
    return redirect("/admin")

@app.route("/admin/remove_active_user/<username>", methods=["POST"])
def remove_active_user(username):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_users WHERE username=%s", (username,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect("/admin")

# ==========================
# ADMIN PANEL
# ==========================
@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    # -------------------------
    # EVENTS
    # -------------------------
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    # -------------------------
    # REGISTRATIONS (USERS)
    # -------------------------
    cursor.execute("""
        SELECT r.id,
               r.name,
               r.email,
               r.status,
               r.attendance_time,
               e.name AS event_name,
               c.category_name
        FROM registrations_new r
        JOIN events e ON r.event_id = e.id
        JOIN event_categories c ON r.category_id = c.id
    """)
    users = cursor.fetchall()

    # -------------------------
    # CATEGORIES (NEW ADDITION)
    # -------------------------
    cursor.execute("""
        SELECT c.id,
               c.category_name,
               e.name AS event_name
        FROM event_categories c
        JOIN events e ON c.event_id = e.id
    """)
    categories = cursor.fetchall()

    # -------------------------
    # SYSTEM USERS (ALL)
    # -------------------------
    cursor.execute("""
        SELECT u.id, u.username, u.email, MAX(a.login_time) as last_login 
        FROM users u 
        LEFT JOIN active_users a ON u.username = a.username 
        GROUP BY u.id, u.username, u.email
        ORDER BY last_login DESC
    """)
    system_users = cursor.fetchall()
    
    # -------------------------
    # COMPETITIONS
    # -------------------------
    cursor.execute("SELECT * FROM competitions")
    competitions = cursor.fetchall()
    
    # -------------------------
    # TECH FESTS
    # -------------------------
    cursor.execute("SELECT * FROM tech_fests")
    tech_fests = cursor.fetchall()

    # -------------------------
    # ACTIVE SESSIONS
    # -------------------------
    active_sessions = cursor.fetchall()

    # -------------------------
    # USER FEEDBACK
    # -------------------------
    cursor.execute("""
        SELECT f.id, f.username, f.message, f.created_at, e.name AS event_name
        FROM event_feedback f
        JOIN events e ON f.event_id = e.id
        ORDER BY f.created_at DESC
    """)
    feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin.html",
        events=events,
        users=users,
        categories=categories,
        system_users=system_users,
        competitions=competitions,
        tech_fests=tech_fests,
        active_sessions=active_sessions,
        feedbacks=feedbacks
        )

@app.route("/admin_analytics")
def admin_analytics():
    if "admin" not in session:
        return redirect("/admin_login")
    return render_template("admin_analytics.html")

@app.route("/api/analytics_data")
def api_analytics_data():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 403
        
    dept_filter = request.args.get("department", "All")
    
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    if dept_filter == "All":
        cursor.execute("SELECT * FROM events")
    else:
        cursor.execute("SELECT * FROM events WHERE department = %s", (dept_filter,))
    events = cursor.fetchall()
    
    event_ids = [e['id'] for e in events]
    total_events = len(events)
    
    total_registrations = 0
    events_labels = []
    events_data = []
    
    if event_ids:
        format_strings = ','.join(['%s'] * len(event_ids))
        cursor.execute(f"SELECT event_id, COUNT(*) as cnt FROM registrations_new WHERE event_id IN ({format_strings}) GROUP BY event_id", tuple(event_ids))
        reg_counts = cursor.fetchall()
        
        reg_dict = {r['event_id']: r['cnt'] for r in reg_counts}
        
        for e in events:
            cnt = reg_dict.get(e['id'], 0)
            total_registrations += cnt
            # Truncate long names for chart labels
            name_label = e['name'][:20] + '...' if len(e['name']) > 20 else e['name']
            events_labels.append(name_label)
            events_data.append(cnt)
    
    cursor.execute("SELECT COUNT(*) as active_cnt FROM active_users")
    active_users = cursor.fetchone()['active_cnt']
    
    if dept_filter == "All":
        cursor.execute("SELECT department, COUNT(*) as cnt FROM events GROUP BY department")
    else:
        cursor.execute("SELECT department, COUNT(*) as cnt FROM events WHERE department = %s GROUP BY department", (dept_filter,))
        
    dept_counts = cursor.fetchall()
    dept_labels = []
    dept_data = []
    for d in dept_counts:
        dept_name = d['department'] if d['department'] else 'Unspecified'
        dept_labels.append(dept_name)
        dept_data.append(d['cnt'])
        
    cursor.close()
    conn.close()
    
    return jsonify({
        "total_registrations": total_registrations,
        "total_events": total_events,
        "active_users": active_users,
        "events_labels": events_labels,
        "events_data": events_data,
        "dept_labels": dept_labels,
        "dept_data": dept_data
    })

@app.route("/request_event_feedback/<int:event_id>")
def request_event_feedback(event_id):
    if "admin" not in session:
        return redirect("/admin_login")
        
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT name FROM events WHERE id=%s", (event_id,))
    event = cursor.fetchone()
    
    if event:
        # Find all registered users for this event
        cursor.execute("SELECT DISTINCT name FROM registrations_new WHERE event_id=%s", (event_id,))
        users = cursor.fetchall()
        
        for u in users:
            notification_title = "Feedback Requested 📝"
            notification_message = f"We hope you enjoyed '{event['name']}'! Please visit the Feedback section to share your thoughts."
            try:
                cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notification_title, notification_message, u["name"]))
            except:
                pass
        conn.commit()
    
    cursor.close()
    conn.close()
    
    return redirect("/admin")
# ==========================
# DOWNLOAD EXCEL
# ==========================
@app.route("/download_registrations")
def download_registrations():

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT r.id,
           r.name,
           r.email,
           r.phone,
           e.name AS event_name,
           c.category_name
    FROM registrations_new r
    JOIN events e ON r.event_id = e.id
    JOIN event_categories c ON r.category_id = c.id
    """)

    data = cursor.fetchall()

    df = pd.DataFrame(data)
    file_path = "registrations.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route("/admin/regenerate_qr")
def admin_regenerate_qr():
    """Regenerate all existing ticket QR codes with enriched data (event, venue, date, category)."""
    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.ticket_id, r.name, r.class, r.team_name,
               e.name as event_name, e.event_date, e.event_time, e.venue,
               c.category_name
        FROM registrations_new r
        JOIN events e ON r.event_id = e.id
        JOIN event_categories c ON r.category_id = c.id
        WHERE r.ticket_id IS NOT NULL
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    count = 0
    for row in rows:
        try:
            generate_ticket_qr(
                row['ticket_id'],
                name=row['name'] or '',
                event_name=row['event_name'] or '',
                category_name=row['category_name'] or '',
                event_date=str(row['event_date'] or ''),
                event_time=str(row['event_time'] or ''),
                venue=row['venue'] or '',
                class_name=row['class'] or '',
                team_name=row['team_name'] or ''
            )
            count += 1
        except Exception as e:
            print(f"QR regen failed for {row['ticket_id']}:", e)

    base_url = get_base_url()
    is_public = base_url.startswith("https://")
    url_note = f"✅ Public URL (ngrok active): <code style='background:#e8f5e9;padding:2px 8px;border-radius:4px;color:#2e7d32;'>{base_url}/verify/&lt;ticket_id&gt;</code>" if is_public else f"⚠️ Local URL only (ngrok not active): <code style='background:#fff3e0;padding:2px 8px;border-radius:4px;color:#e65100;'>{base_url}/verify/&lt;ticket_id&gt;</code>"
    return f"""
    <div style='font-family:sans-serif;text-align:center;margin-top:80px;max-width:600px;margin-left:auto;margin-right:auto;'>
      <h2 style='color:#10b981;'>✅ QR Codes Regenerated</h2>
      <p style='color:#555; margin-top:8px;'>{count} ticket QR code(s) updated.</p>
      <p style='font-size:0.9rem; margin-top:10px;'>{url_note}</p>
      {'<p style="color:#888;font-size:0.8rem;margin-top:8px;">Add NGROK_AUTHTOKEN to .env to enable public scanning from any phone.</p>' if not is_public else '<p style="color:#10b981;font-size:0.85rem;margin-top:8px;">🌍 Anyone can scan these QR codes from any network!</p>'}
      <a href='/admin' style='display:inline-block;margin-top:20px;color:#6366f1;font-weight:bold;'>← Back to Admin</a>
    </div>"""

@app.route("/admin/scan_ticket", methods=["GET", "POST"])
def admin_scan_ticket():
    if "admin" not in session:
        return redirect("/admin_login")
        
    message = None
    success = False
    reg_info = None
    
    if request.method == "POST":
        ticket_id = request.form.get("ticket_id")
        if ticket_id:
            ticket_id = ticket_id.strip().upper()
            conn = get_db_coonection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, e.name as event_name, e.venue, e.event_date, e.event_time,
                       c.category_name
                FROM registrations_new r
                JOIN events e ON r.event_id = e.id
                JOIN event_categories c ON r.category_id = c.id
                WHERE r.ticket_id=%s
            """, (ticket_id,))
            reg = cursor.fetchone()
            
            if reg:
                reg_info = reg
                if reg['status'] == 'Attended':
                    message = f"⚠️ Ticket already used — {reg['name']} was marked Attended earlier."
                    success = False
                else:
                    # We no longer mark it attended automatically.
                    # Instead, we show the details and a button to mark it.
                    message = f"✅ Ticket Found! Verify registrant details below."
                    success = True
            else:
                message = "❌ Invalid Ticket ID — no matching registration found."
                
            cursor.close()
            conn.close()
            
    return render_template("admin_scan.html", message=message, success=success, reg_info=reg_info)

@app.route("/admin/mark_attendance/<ticket_id>", methods=["POST"])
def mark_attendance(ticket_id):
    if "admin" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    ticket_id = ticket_id.upper()
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if already marked
    cursor.execute("SELECT status, attendance_time FROM registrations_new WHERE ticket_id=%s", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Invalid ticket ID"}), 404
    
    if row['status'] == 'Attended':
        cursor.close()
        conn.close()
        ts = row['attendance_time'].strftime('%d %b %Y %I:%M %p') if row['attendance_time'] else 'earlier'
        return jsonify({"success": False, "already": True, "error": f"Already marked Present at {ts}"})
    
    now_ts = datetime.now()
    cursor.execute(
        "UPDATE registrations_new SET status='Attended', attendance_time=%s WHERE ticket_id=%s",
        (now_ts, ticket_id)
    )
    
    # Send a notification to the user
    try:
        # We need the user's name and event name for the notification
        cursor.execute("SELECT r.name, r.account_username, e.name as event_name FROM registrations_new r LEFT JOIN events e ON r.event_id = e.id WHERE r.ticket_id=%s", (ticket_id,))
        u_row = cursor.fetchone()
        if u_row:
            user_name = u_row.get('account_username') or u_row.get('name') or "Attendee"
            event_name = u_row.get('event_name') or "the event"
            notif_title = "✅ Attendance Marked"
            notif_message = f"Thanks for attending {event_name}! Your entry was successfully verified."
            cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notif_title, notif_message, user_name))
    except Exception as e:
        print("Failed to send attendance notification:", e)

    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True, "timestamp": now_ts.strftime('%d %b %Y %I:%M %p')})

# ==========================
# PUBLIC /verify/ — QR SCAN LANDING PAGE
# Scanning QR opens this page. Shows ticket info.
# Marking present requires admin login OR staff PIN.
# ==========================
@app.route("/verify/<ticket_id>")
def verify_ticket(ticket_id):
    ticket_id = ticket_id.upper()
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.ticket_id, r.name, r.email, r.phone, r.branch, r.class, r.team_name,
               r.status, r.payment_status, r.transaction_id, r.attendance_time,
               e.name as event_name, e.venue, e.event_date, e.event_time, e.description,
               c.category_name
        FROM registrations_new r
        JOIN events e ON r.event_id = e.id
        JOIN event_categories c ON r.category_id = c.id
        WHERE r.ticket_id = %s
    """, (ticket_id,))
    ticket = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not ticket:
        return render_template("verify.html", ticket=None, error="Invalid or expired ticket ID.")
    
    is_admin = "admin" in session
    return render_template("verify.html", ticket=ticket, is_admin=is_admin, error=None)

# ==========================
# /mark_present — Mark attendance via AJAX
# Admin session OR valid STAFF_PIN required
# ==========================
@app.route("/mark_present", methods=["POST"])
def mark_present():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data"}), 400
    
    ticket_id  = (data.get("ticket_id") or "").strip().upper()
    staff_pin  = (data.get("staff_pin") or "").strip()
    
    if not ticket_id:
        return jsonify({"success": False, "error": "Ticket ID required"}), 400
    
    # Security: must be admin OR correct staff PIN
    is_admin = "admin" in session
    pin_ok   = staff_pin == STAFF_PIN
    
    if not is_admin and not pin_ok:
        return jsonify({"success": False, "error": "Unauthorized — invalid PIN"}), 403
    
    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status, attendance_time FROM registrations_new WHERE ticket_id=%s", (ticket_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Ticket not found"}), 404
    
    if row['status'] == 'Attended':
        cursor.close()
        conn.close()
        ts = row['attendance_time'].strftime('%d %b %Y %I:%M %p') if row['attendance_time'] else 'earlier'
        return jsonify({"success": False, "already": True,
                        "error": f"Already marked Present at {ts}"})
    
    now_ts = datetime.now()
    cursor.execute(
        "UPDATE registrations_new SET status='Attended', attendance_time=%s WHERE ticket_id=%s",
        (now_ts, ticket_id)
    )
    
    # Send a notification to the user
    try:
        # We need the user's name and event name for the notification
        cursor.execute("SELECT r.name, r.account_username, e.name as event_name FROM registrations_new r LEFT JOIN events e ON r.event_id = e.id WHERE r.ticket_id=%s", (ticket_id,))
        u_row = cursor.fetchone()
        if u_row:
            user_name = u_row.get('account_username') or u_row.get('name') or "Attendee"
            event_name = u_row.get('event_name') or "the event"
            notif_title = "✅ Attendance Marked"
            notif_message = f"Thanks for attending {event_name}! Your entry was successfully verified."
            cursor.execute("INSERT INTO notifications (title, message, username) VALUES (%s, %s, %s)", (notif_title, notif_message, user_name))
    except Exception as e:
        print("Failed to send attendance notification:", e)
        
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True, "timestamp": now_ts.strftime('%d %b %Y %I:%M %p')})

# ==========================
# PUBLIC TICKET VIEW  (scan QR -> get ticket info like GPay)
# Event staff mark attendance with a staff PIN — no admin login needed
# ==========================
STAFF_PIN = os.getenv("STAFF_PIN", "EVENT2026")

@app.route("/ticket/<ticket_id>", methods=["GET", "POST"])
def view_ticket(ticket_id):
    ticket_id = ticket_id.upper()
    attend_msg = None
    attend_success = None

    conn = get_db_coonection()
    cursor = conn.cursor(dictionary=True)

    # Event staff taps "Mark as Attended" and enters PIN
    if request.method == "POST":
        entered_pin = request.form.get("staff_pin", "").strip()
        if entered_pin == STAFF_PIN:
            cursor.execute("SELECT status FROM registrations_new WHERE ticket_id=%s", (ticket_id,))
            row = cursor.fetchone()
            if row:
                if row['status'] == 'Attended':
                    attend_msg = "Already marked Attended earlier."
                    attend_success = False
                else:
                    cursor.execute("UPDATE registrations_new SET status='Attended' WHERE ticket_id=%s", (ticket_id,))
                    conn.commit()
                    attend_msg = "Entry Confirmed! Marked as Attended."
                    attend_success = True
            else:
                attend_msg = "Ticket not found."
                attend_success = False
        else:
            attend_msg = "Wrong staff PIN. Please try again."
            attend_success = False

    cursor.execute("""
        SELECT r.ticket_id, r.name, r.email, r.phone, r.branch, r.class, r.team_name,
               r.status, r.payment_status, r.transaction_id,
               e.name as event_name, e.venue, e.event_date, e.event_time, e.description,
               c.category_name
        FROM registrations_new r
        JOIN events e ON r.event_id = e.id
        JOIN event_categories c ON r.category_id = c.id
        WHERE r.ticket_id = %s
    """, (ticket_id,))
    ticket = cursor.fetchone()
    cursor.close()
    conn.close()

    if not ticket:
        return "<h2 style='text-align:center;margin-top:80px;font-family:sans-serif'>Invalid or expired ticket ID.</h2>", 404
    return render_template("ticket_view.html", ticket=ticket, attend_msg=attend_msg, attend_success=attend_success)

# ==========================
# BACKGROUND REMINDERS (1 HOUR)
# ==========================
def parse_event_datetime(evt_date, evt_time_str):
    try:
        date_str = str(evt_date)
        evt_time_str = evt_time_str.strip().upper()
        
        if 'AM' in evt_time_str or 'PM' in evt_time_str:
            t = datetime.strptime(evt_time_str, '%I:%M %p').time()
        else:
            if len(evt_time_str.split(':')[0]) == 1:
                evt_time_str = "0" + evt_time_str
            t = datetime.strptime(evt_time_str, '%H:%M').time()
            
        return datetime.strptime(f"{date_str} {t.strftime('%H:%M:%S')}", '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print("Time parse error:", e)
        return None

def check_and_send_1h_reminders():
    while True:
        try:
            conn = get_db_coonection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM events WHERE (reminder_1h_sent IS NULL OR reminder_1h_sent = FALSE)")
            events = cursor.fetchall()
            
            now = datetime.now()
            
            for evt in events:
                if not evt['event_date'] or not evt['event_time']:
                    continue
                    
                evt_dt = parse_event_datetime(evt['event_date'], evt['event_time'])
                if not evt_dt:
                    continue
                    
                time_diff = evt_dt - now
                
                # If event is within 1 hour
                if timedelta(seconds=0) < time_diff <= timedelta(hours=1):
                    cursor.execute("SELECT * FROM registrations_new WHERE event_id=%s", (evt['id'],))
                    regs = cursor.fetchall()
                    
                    if regs:
                        try:
                            server = smtplib.SMTP("smtp.gmail.com", 587)
                            server.starttls()
                            server.login("atharvkudtarkar4406@gmail.com", "dxnt tdxx egdg sgua")
                            
                            for r in regs:
                                msg_text = f"Hi {r['name']},\n\nJust a quick reminder that '{evt['name']}' is starting in less than 1 hour!\n\nVenue: {evt['venue']}\nTime: {evt['event_time']}\n\nSee you soon!"
                                msg = MIMEText(msg_text)
                                msg["Subject"] = f"Reminder: {evt['name']} starts in <1 hour!"
                                msg["From"] = "atharvkudtarkar4406@gmail.com"
                                msg["To"] = r['email']
                                server.send_message(msg)
                            
                            server.quit()
                        except Exception as email_err:
                            print("Reminder Email failed:", email_err)
                            
                    cursor.execute("UPDATE events SET reminder_1h_sent = TRUE WHERE id=%s", (evt['id'],))
                    conn.commit()
            
            cursor.close()
            conn.close()
        except Exception as e:
            print("Reminder thread error:", e)
            
        time.sleep(300)

def start_background_threads():
    if not os.environ.get('PYTEST_CURRENT_TEST') and not app.config.get('TESTING'):
        try:
            reminder_thread = threading.Thread(target=check_and_send_1h_reminders, daemon=True)
            reminder_thread.start()
            
            deadline_thread = threading.Thread(target=check_registration_deadlines, daemon=True)
            deadline_thread.start()
            
            ngrok_thread = threading.Thread(target=start_ngrok_tunnel, daemon=True)
            ngrok_thread.start()
        except Exception as err:
            print("Background threads initialization warning:", err)

if __name__ == "__main__":
    start_background_threads()
    app.run(debug=True, host='0.0.0.0')
