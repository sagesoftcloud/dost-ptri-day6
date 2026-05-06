"""
DOST PTRI Day 6 — Sample CI/CD Application
A simple Flask health-check API to demonstrate CodeBuild + CodeDeploy workflow.
"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "DOST PTRI Day 6 — CI/CD Sample App", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
