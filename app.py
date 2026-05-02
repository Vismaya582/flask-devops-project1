from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0")
APP_ENV = os.getenv("APP_ENV", "development")


@app.route("/")
def home():
    return jsonify({
        "message": "Hello from my DevOps project - Vismaya - v2",
        "version": APP_VERSION,
        "environment": APP_ENV
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/info")
def info():
    return jsonify({
        "app": "flask-devops-app",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "endpoints": ["/", "/health", "/info"]
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)