import requests
import os

SERVER = "http://localhost:5000"
FILE_PATH = "xyz.png"
CHUNK_SIZE = 1024 * 1024  # 1 MB

def upload_file(file_path):
    # Start a session
    res = requests.post(f"{SERVER}/upload/start")
    session_id = res.json()["session_id"]
    print("Started session:", session_id)

    offset = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            headers = {"X-Upload-Offset": str(offset)}
            try:
                res = requests.put(f"{SERVER}/upload/{session_id}", headers=headers, data=chunk)
                res.raise_for_status()
            except requests.exceptions.RequestException as e:
                print("Upload failed at offset", offset)
                # simulate retry
                res = requests.get(f"{SERVER}/upload/{session_id}/status")
                offset = res.json()["offset"]
                f.seek(offset)
                continue

            offset += len(chunk)
            print(f"Uploaded {offset} bytes")

    # Finalize
    res = requests.post(f"{SERVER}/upload/{session_id}/complete")
    print("Upload complete:", res.json())

if __name__ == "__main__":
    # Create a dummy large file
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "wb") as f:
            f.write(os.urandom(5 * CHUNK_SIZE))  # ~5MB file

    upload_file(FILE_PATH)
