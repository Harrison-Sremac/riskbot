#webhook.py
import os
from flask import Flask, Blueprint, request, jsonify, abort # type: ignore
from send import send_email
from parse_alert import rewrite_alert_with_openai, generate_html_email
from dotenv import load_dotenv # type: ignore
load_dotenv()

#getting local environment variables
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")



webhook_bp = Blueprint("webhook", __name__)


def verify_webhook_secret(req):
    token = req.headers.get("X-BlackKite-Webhook-Api-Key")
    print("Expected:", WEBHOOK_SECRET)
    print("Received:", token)
    if not token or token != WEBHOOK_SECRET:
        print("Webhook secret verification failed")
        abort(403)


@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    verify_webhook_secret(request)

    raw_data = request.json
    print("Received JSON:", raw_data)

    if not raw_data:
        return jsonify({"error": "No JSON payload"}), 400

    try:
        event = raw_data.get("Event", "No event provided")
        timestamp = raw_data.get("Timestamp", "No timestamp provided")
        data = raw_data.get("Data") or {}
        company = data.get("CompanyName", "Unknown")
        findings = data.get("Findings") or [{}]
        finding = findings[0]

        # Safely get finding fields with defaults
        title = finding.get("Title", "No title provided")
        module = finding.get("Module", "No module provided")
        severity = finding.get("Severity", "Unknown")
        control_id = finding.get("ControlId", "N/A")
        url = finding.get("Url", "#")

        # Add company name into finding for email template if needed
        finding["CompanyName"] = company

        alert_text = f"""
Event: {event}
Company: {company}
Timestamp: {timestamp}

Finding:
- Title: {title}
- Module: {module}
- Severity: {severity}
- Control ID: {control_id}
- URL: {url}

"""

        summary = rewrite_alert_with_openai(alert_text)
        html_body = generate_html_email(summary, finding)

        subject = f"[{severity}] New Finding for {company}: {title}"

        send_email(subject, html_body)
        print("Processed webhook and sent email.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error parsing webhook:", e)
        return jsonify({"error": "Invalid payload"}), 400