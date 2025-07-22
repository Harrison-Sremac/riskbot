# run.py

from flask import Flask # type: ignore
from webhook import webhook_bp

app = Flask(__name__)
app.register_blueprint(webhook_bp)

if __name__ == "__main__":
    app.run(port=5001, debug=True)