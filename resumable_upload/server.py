from flask import Flask, request, jsonify, send_file
import os
import uuid

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

sessions = {}  # session_id -> {'path': ..., 'offset': ...}

@app.route("/upload/start", methods=["POST"])
def start_upload():
    session_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.part")
    sessions[session_id] = {"path": file_path, "offset": 0}
    with open(file_path, "wb") as f:
        pass  # create empty file
    return jsonify({"session_id": session_id})

@app.route("/upload/<session_id>", methods=["PUT"])
def upload_chunk(session_id):
    if session_id not in sessions:
        return "Invalid session", 404

    session = sessions[session_id]
    start = int(request.headers.get("X-Upload-Offset", 0))
    if start != session["offset"]:
        return f"Wrong offset. Expected {session['offset']}", 409

    chunk = request.data
    with open(session["path"], "ab") as f:
        f.write(chunk)
    session["offset"] += len(chunk)
    return jsonify({"uploaded": session["offset"]})

@app.route("/upload/<session_id>/status", methods=["GET"])
def get_status(session_id):
    if session_id not in sessions:
        return "Invalid session", 404
    return jsonify({"offset": sessions[session_id]["offset"]})

@app.route("/upload/<session_id>/complete", methods=["POST"])
def finalize_upload(session_id):
    if session_id not in sessions:
        return "Invalid session", 404
    # Rename file to final version
    final_path = os.path.join(UPLOAD_DIR, f"{session_id}.complete")
    os.rename(sessions[session_id]["path"], final_path)
    del sessions[session_id]
    return jsonify({"status": "completed", "file": final_path})

if __name__ == "__main__":
    app.run(port=5000)
