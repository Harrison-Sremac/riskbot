# blackkite/webhook_server/webhook.py

from flask import Blueprint, request, jsonify
from utils.parse_alert import parse_alert
from emailer.send import send_email

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received webhook:", data)

    parsed = parse_alert(data)
    email_body = f"Risk Alert: {parsed['title']}\n\nDetails:\n{parsed['details']}"

    send_email(subject=parsed['title'], body=email_body)
    return jsonify({"status": "received"}), 200