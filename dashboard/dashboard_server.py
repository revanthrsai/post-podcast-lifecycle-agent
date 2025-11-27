from flask import Flask, send_file, render_template, abort, jsonify
import os, json

app = Flask(__name__, template_folder='templates', static_folder='static')

# PATHS
ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")

def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception:
        return []

def list_json_files(path):
    files = []
    for f in safe_listdir(path):
        if not f.lower().endswith(".json"):
            continue
        full = os.path.join(path, f)
        if os.path.isdir(full):
            continue
        files.append(f)
    return files

def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None

def is_safe_path(basedir, path):
    abs_base = os.path.abspath(basedir)
    abs_target = os.path.abspath(path)
    return abs_target.startswith(abs_base)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/list")
def api_list():
    files = list_json_files(OUTPUT_DIR)
    return jsonify({"files": files})

@app.route("/api/json/<path:filename>")
def get_json(filename):
    candidate = os.path.abspath(os.path.join(OUTPUT_DIR, filename))
    if not is_safe_path(OUTPUT_DIR, candidate) or not os.path.isfile(candidate):
        return abort(404)
    
    data = load_json_safe(candidate)
    if data is None:
        return jsonify({"error": "Could not load file"}), 500
    return jsonify(data)

@app.route("/download/<path:filename>")
def download_file(filename):
    candidate = os.path.abspath(os.path.join(OUTPUT_DIR, filename))
    if not is_safe_path(OUTPUT_DIR, candidate) or not os.path.isfile(candidate):
        return abort(404)
    return send_file(candidate, as_attachment=True)

if __name__ == "__main__":
    print(f"Serving dashboard — outputs dir: {OUTPUT_DIR}")
    app.run(debug=True, use_reloader=False)
