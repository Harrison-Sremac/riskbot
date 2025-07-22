#webhook.py
import os
from flask import Flask, Blueprint, request, jsonify, abort  # type: ignore
from send import send_email
from parse_alert import rewrite_alert_with_openai, generate_html_email
from dotenv import load_dotenv  # type: ignore
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
        event = raw_data.get("Event")
        timestamp = raw_data.get("Timestamp")
        data = raw_data.get("Data") or {}
        company = data.get("CompanyName", "Unknown")
        findings = data.get("Findings", [])

        subject = f"[{event or 'Unknown Event'}] Update for {company}"

        # CASE: Finding Alert
        if findings:
            finding = findings[0]
            # Ensure all required fields are present for downstream functions
            finding["CompanyName"] = company
            finding.setdefault("InsertDate", timestamp)
            finding.setdefault("Title", "No Title")
            finding.setdefault("Module", "Unknown")
            finding.setdefault("Severity", "Unknown")
            finding.setdefault("ControlId", "N/A")
            finding.setdefault("Url", "")
            # Log any missing/None fields for debugging
            required_fields = ["Title", "Module", "Severity", "ControlId", "Url"]
            for field in required_fields:
                if finding.get(field) is None:
                    print(f"Warning: Field '{field}' is None in finding: {finding}")

            alert_text = f"""
Event: {event}
Company: {company}
Timestamp: {timestamp}

Finding:
- Title: {finding.get("Title") or 'No Title'}
- Module: {finding.get("Module") or 'Unknown'}
- Severity: {finding.get("Severity") or 'Unknown'}
- Control ID: {finding.get("ControlId") or 'N/A'}
- URL: {finding.get("Url") or ''}
"""
            summary = rewrite_alert_with_openai(alert_text)
            html_body = generate_html_email(summary, finding)
            subject = f"[{finding.get('Severity') or 'Unknown'}] New Finding for {company}: {finding.get('Title') or 'No Title'}"

        # CASE: Focus Tag Trigger
        elif event == "TestFocusTagIsAssociatedWithACompany" and data.get("Tags"):
            tag_name = data["Tags"][0].get("TagName", "Unknown")
            url = data.get("Url", "")
            summary = f"A new focus tag '<strong>{tag_name}</strong>' has been associated with {company}."
            html_body = generate_html_email(summary, {"CompanyName": company, "InsertDate": timestamp, "Url": url, "Module": "Focus Tag Monitor", "Category": tag_name, "Severity": "Informational", "ControlId": "TAG-001", "FocusTag": tag_name, "Description": f"The tag '{tag_name}' has been newly associated.", "RecommendedAction": ["Review the implications of the tag."], "Notes": ""})
            subject = f"[Tag Alert] {tag_name} associated with {company}"

        # CASE: RSI Trigger
        elif event == "TestRansomwareSusIndexIsAboveThreshold":
            current = data.get("CurrentIndex")
            previous = data.get("PreviousIndex")
            url = data.get("Url", "")
            summary = f"Ransomware Susceptibility Index (RSI) for <strong>{company}</strong> has risen to <strong>{current}</strong> (previous: {previous})."
            html_body = generate_html_email(summary, {"CompanyName": company, "InsertDate": timestamp, "Url": url, "Module": "RSI Monitor", "Category": "RSI", "Severity": "Medium", "ControlId": "RSI-THRESHOLD", "FocusTag": "RSI", "Description": f"Current RSI is {current}, previously {previous}.", "RecommendedAction": ["Investigate root causes of increased RSI.", "Notify internal stakeholders.", "Review system defenses."], "Notes": ""})
            subject = f"[RSI Alert] Elevated RSI for {company}"

        else:
            # Fallback notification
            summary = f"Webhook event '{event}' received for {company}."
            html_body = generate_html_email(summary, {"CompanyName": company, "InsertDate": timestamp, "Url": "", "Module": event, "Category": "General", "Severity": "Low", "ControlId": "GEN-001", "FocusTag": "General", "Description": "General webhook event received.", "RecommendedAction": ["Review incoming webhook."], "Notes": "This is a fallback message.", })
            subject = f"[Notification] Event received for {company}"

        send_email(subject, html_body)
        print("Processed webhook and sent email.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error parsing webhook:", e)
        return jsonify({"error": "Invalid payload"}), 400