#webhook.py
import os
from flask import Flask, Blueprint, request, jsonify, abort
from send import send_email
from parse_alert import rewrite_alert_with_openai, generate_html_email
from dotenv import load_dotenv
load_dotenv()

#getting local environment variables
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")



webhook_bp = Blueprint("webhook", __name__)


def verify_webhook_secret(req):
    # check headers for the secret token
    token = req.headers.get("X-Webhook-Secret")
    if not token or token != WEBHOOK_SECRET:
        print("Webhook secret verification failed")
        abort(403)




@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    verify_webhook_secret(request)

    raw_data = request.json
    if not raw_data:
        return jsonify({"error": "No JSON payload"}), 400

    try:
        body = raw_data["webhook_action"]["body"]
        event = body["Event"]
        timestamp = body["Timestamp"]
        company = body["Data"]["CompanyName"]
        finding = body["Data"]["Findings"][0]  
        finding["CompanyName"] = company

        # Build a plain-text summary of the alert
        alert_text = f"""
Event: {event}
Company: {company}
Timestamp: {timestamp}

Finding:
- Title: {finding["Title"]}
- Module: {finding["Module"]}
- Severity: {finding["Severity"]}
- Control ID: {finding["ControlId"]}
- URL: {finding["Url"]}

"""

        summary = rewrite_alert_with_openai(alert_text)
        html_body = generate_html_email(summary, finding)


        # Build subject
        subject = f"[{finding['Severity']}] New Finding for {company}: {finding['Title']}"

        # Send the email
        send_email(subject, html_body)
        print("Processed webhook and sent email.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error parsing webhook:", e)
        return jsonify({"error": "Invalid payload"}), 400

