"""
Mablast-Email-Blaster
A powerful Flask-based mass email sender with dynamic variables and SMTP management
"""

from flask import Flask, render_template, request, redirect, jsonify
from email_sender import send_email
import os
from dotenv import load_dotenv
from supabase_client import get_smtp_config, log_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase_client import get_all_smtp_configs, add_smtp_config, delete_smtp_config, get_smtp_config_by_id

import time

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Mablast-Email-Blaster Configuration
APP_NAME = "Mablast-Email-Blaster"
VERSION = "1.0.0"

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        raw_lines = request.form["to_emails"].strip().split("\n")
        subject = request.form["subject"]
        body_template = request.form["body"]
        body_type = request.form["body_type"]

        smtp = get_smtp_config()
        if not smtp:
            results.append({"email": "N/A", "status": "failed", "error": "SMTP config not found"})
            return render_template("index.html", results=results)

        for line in raw_lines:
            parts = [p.strip() for p in line.split(",")]
            if not parts or len(parts[0]) < 5 or "@" not in parts[0]:
                results.append({"email": parts[0] if parts else "N/A", "status": "failed", "error": "Email tidak valid"})
                continue

            to_email = parts[0]
            # Gantikan <variable1>, <variable2>, dst dengan value masing-masing
            body = body_template
            for i, val in enumerate(parts[1:], start=1):
                body = body.replace(f"<variable{i}>", val)

                if len(parts[1:]) == 0:
                    body = body_template  # tidak ada masking, kirim apa adanya
                else:
                    for i, val in enumerate(parts[1:], start=1):
                        body = body.replace(f"<variable{i}>", val)


            msg = MIMEMultipart()
            msg["From"] = smtp["smtp_user"]
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, body_type))

            try:
                with smtplib.SMTP(smtp["smtp_host"], smtp["smtp_port"]) as server:
                    server.starttls()
                    server.login(smtp["smtp_user"], smtp["smtp_pass"])
                    server.sendmail(smtp["smtp_user"], to_email, msg.as_string())
                log_email(to_email, subject, body, body_type, "success")
                results.append({"email": to_email, "status": "success"})
            except Exception as e:
                log_email(to_email, subject, body, body_type, "failed", str(e))
                results.append({"email": to_email, "status": "failed", "error": str(e)})

            time.sleep(0.8)  # delay biar animasi terasa
    return render_template("index.html", results=results, get_all_configs=get_all_smtp_configs())

@app.route("/send-one", methods=["POST"])
def send_one_email():
    data = request.get_json()
    smtp_id = data["smtp_id"]
    line = data["line"]
    subject = data["subject"]
    body_template = data["body"]
    is_html = data["is_html"]

    smtp = get_smtp_config_by_id(smtp_id)

    parts = [p.strip() for p in line.split(",")]
    if not parts or "@" not in parts[0]:
        return jsonify({"email": parts[0] if parts else "N/A", "status": "failed", "error": "Format salah"})

    email = parts[0]
    body = body_template
    for i, val in enumerate(parts[1:], start=1):
        body = body.replace(f"<variable{i}>", val)

    try:
        send_email(
            smtp_user=smtp["smtp_user"],
            smtp_pass=smtp["smtp_pass"],
            smtp_host=smtp["smtp_host"],
            smtp_port=smtp["smtp_port"],
            to=email,
            subject=subject,
            body=body,
            is_html=is_html
        )
        log_email(email, subject, body, "success", smtp["name"])
        return jsonify({"email": email, "status": "success"})
    except Exception as e:
        log_email(email, subject, body, "failed", smtp["name"])
        return jsonify({"email": email, "status": "failed", "error": str(e)})

@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "smtp_host": request.form["smtp_host"],
            "smtp_port": int(request.form["smtp_port"]),
            "smtp_user": request.form["smtp_user"],
            "smtp_pass": request.form["smtp_pass"]
        }
        add_smtp_config(data)
    configs = get_all_smtp_configs()
    return render_template("config.html", configs=configs)

@app.route("/config/delete/<config_id>")
def delete_config(config_id):
    delete_smtp_config(config_id)
    return redirect("/config")

if __name__ == "__main__":
    print(f"🚀 Starting {APP_NAME} v{VERSION}")
    print(f"📧 Mass Email Blaster with Dynamic Variables")
    print(f"🌐 Server running on: http://127.0.0.1:5000")
    print("-" * 50)
    app.run(debug=True)