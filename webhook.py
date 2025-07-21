# blackkite/webhook_server/webhook.py
import os
from flask import Flask, Blueprint, request, jsonify, abort # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
webhook_bp = Blueprint("webhook", __name__)
print("Loaded secret:", WEBHOOK_SECRET)

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        print("Received webhook request")
        return 'success', 200
    else:
        print("Invalid request method")
        abort(400)

if __name__ == "__main__":
    app.run()

   