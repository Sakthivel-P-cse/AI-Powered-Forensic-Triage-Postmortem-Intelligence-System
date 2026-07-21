import json
import httpx
from jose import jwt
from pathlib import Path

BASE_URL = "http://localhost:8000/api"
TOKEN = jwt.encode({"sub": "admin@forensic.local", "role": "ADMIN", "exp": 9999999999}, "change-me-256-bit-random", algorithm="HS256")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

SAMPLE = Path("/app/sample_data")
CASE_ID = "CR-2024-00471"

def main():
    with httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=120.0) as client:
        # 1. Create Case
        print("Creating case...")
        res = client.post("/cases", json={
            "id": CASE_ID,
            "title": "Flat 4B Block B — Suspicious Death",
            "status": "IN_TRIAGE"
        })
        if res.status_code == 201:
            print("Case created!")
        elif res.status_code == 400 and "exists" in res.text:
            print("Case already exists!")
        else:
            print(f"Case creation failed: {res.status_code} {res.text}")
        
        # 2. Ingest CCTV
        print("Ingesting CCTV...")
        cctv_data = json.loads((SAMPLE / "cctv_logs.json").read_text())
        cctv_payload = []
        for r in cctv_data:
            cctv_payload.append({
                "camera_id": r["camera_id"],
                "location": r["location"],
                "event_timestamp": r["timestamp"],
                "event_type": r["event_type"],
                "attributes": r.get("attributes", {})
            })
        res = client.post(f"/cases/{CASE_ID}/cctv", json=cctv_payload)
        print(f"CCTV: {res.status_code} {res.text}")

        # 3. Ingest GPS
        print("Ingesting GPS...")
        gps_data = json.loads((SAMPLE / "gps_logs.json").read_text())
        gps_payload = []
        for r in gps_data:
            gps_payload.append({
                "subject_id": r["subject_id"],
                "timestamp": r["timestamp"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "accuracy_m": r.get("accuracy_m"),
                "source": r.get("source")
            })
        res = client.post(f"/cases/{CASE_ID}/gps", json=gps_payload)
        print(f"GPS: {res.status_code} {res.text}")

        # 4. Ingest Calls
        print("Ingesting Calls...")
        calls_data = json.loads((SAMPLE / "call_logs.json").read_text())
        res = client.post(f"/cases/{CASE_ID}/calls", json=calls_data)
        print(f"Calls: {res.status_code} {res.text}")

        # 5. Upload Autopsy
        print("Uploading Autopsy...")
        with open(SAMPLE / "autopsy_report.txt", "rb") as f:
            files = {"file": ("autopsy_report.txt", f, "text/plain")}
            data = {"case_id": CASE_ID, "file_type": "autopsy"}
            res = client.post("/evidence/upload", data=data, files=files)
            print(f"Autopsy: {res.status_code} {res.text}")
            
        print("Done!")

if __name__ == "__main__":
    main()
