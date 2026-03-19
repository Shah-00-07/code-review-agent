"""
Code Review Agent — Web Dashboard
Flask backend serving the review API
"""

import os
import sys
import json
import glob
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Add project root to path so we can import core.analyzer
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.analyzer import perform_code_review

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow cross-origin requests from Firebase Hosting

# Use /tmp on cloud platforms (Render, Cloud Functions, etc.)
if os.environ.get("RENDER") or os.environ.get("K_SERVICE"):
    REVIEWS_DIR = "/tmp/reviews"
else:
    REVIEWS_DIR = os.path.join(PROJECT_ROOT, ".agent", "reviews")

os.makedirs(REVIEWS_DIR, exist_ok=True)


@app.route("/")
def index():
    """Serve the main dashboard."""
    return render_template("index.html")


@app.route("/api/review", methods=["POST"])
def review_code():
    """Run a code review on submitted code or file."""
    try:
        data = request.json
        code = data.get("code", "")
        filename = data.get("filename", "untitled.py")

        if not code.strip():
            return jsonify({"error": "No code provided."}), 400

        start = time.time()
        report = perform_code_review(code, file_name=filename)
        elapsed = round(time.time() - start, 2)

        # Save the review artifact
        ts = int(time.time())
        artifact_name = f"web_review_{filename}_{ts}.md"
        artifact_path = os.path.join(REVIEWS_DIR, artifact_name)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(f"# Web Review: {filename}\nDate: {datetime.now().isoformat()}\n\n{report}")

        return jsonify({
            "report": report,
            "elapsed": elapsed,
            "artifact": artifact_name,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return jsonify({
            "report": f"### Server Error\n\nThe backend crashed while processing your review.\n\n**Error:** `{str(e)}`\n\n**Traceback:**\n```\n{tb}\n```",
            "elapsed": 0,
            "artifact": "",
            "timestamp": datetime.now().isoformat()
        })


@app.route("/api/review-file", methods=["POST"])
def review_file():
    """Review a file from the project directory by path."""
    data = request.json
    filepath = data.get("filepath", "")

    # Resolve relative to project root
    full_path = os.path.join(PROJECT_ROOT, filepath)
    if not os.path.exists(full_path):
        return jsonify({"error": f"File not found: {filepath}"}), 404

    with open(full_path, "r", encoding="utf-8") as f:
        code = f.read()

    start = time.time()
    report = perform_code_review(code, file_name=os.path.basename(filepath))
    elapsed = round(time.time() - start, 2)

    # Save artifact
    ts = int(time.time())
    artifact_name = f"web_review_{os.path.basename(filepath)}_{ts}.md"
    artifact_path = os.path.join(REVIEWS_DIR, artifact_name)
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(f"# Web Review: {filepath}\nDate: {datetime.now().isoformat()}\n\n{report}")

    return jsonify({
        "report": report,
        "code": code,
        "elapsed": elapsed,
        "artifact": artifact_name,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/history")
def review_history():
    """Return list of past review artifacts."""
    reviews = []
    if os.path.exists(REVIEWS_DIR):
        files = sorted(glob.glob(os.path.join(REVIEWS_DIR, "*.md")), key=os.path.getmtime, reverse=True)
        for f in files[:30]:
            stat = os.stat(f)
            reviews.append({
                "name": os.path.basename(f),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    return jsonify(reviews)


@app.route("/api/history/<filename>")
def get_review(filename):
    """Return the content of a specific review artifact."""
    filepath = os.path.join(REVIEWS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Review not found"}), 404
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"name": filename, "content": content})


@app.route("/api/files")
def list_project_files():
    """List reviewable files in the project."""
    files = []
    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        # Skip hidden and agent directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "web", "node_modules")]
        for fn in filenames:
            if fn.endswith((".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css")):
                rel = os.path.relpath(os.path.join(root, fn), PROJECT_ROOT)
                files.append(rel)
    return jsonify(files)


@app.route("/api/status")
def agent_status():
    """Return the agent status."""
    has_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    review_count = len(glob.glob(os.path.join(REVIEWS_DIR, "*.md")))
    
    sdk_version = "unknown"
    try:
        import google.generativeai
        sdk_version = google.generativeai.__version__
    except:
        pass

    return jsonify({
        "gemini_connected": has_key,
        "review_count": review_count,
        "model": "gemini-1.5-flash-latest" if has_key else "mock (offline)", # Fixed model name
        "sdk_version": sdk_version,
        "project_root": PROJECT_ROOT,
        "deploy_ts": "2026-03-19-V1" # Added a version tag
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 55)
    print("  CODE REVIEW AGENT — Web Dashboard")
    print(f"  http://localhost:{port}")
    print("=" * 55 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
