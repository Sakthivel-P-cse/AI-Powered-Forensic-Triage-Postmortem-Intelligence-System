"""Coverage for endpoints added in the second backend pass."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, email: str) -> str:
    res = client.post("/auth/login", data={"username": email, "password": "demo"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def auth(t: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {t}"}


# ---------- Call analyzer ----------
def test_call_tower_gps_mismatch(client: TestClient):
    t = _login(client, "analyst@forensic.local")
    body = {
        "calls": [
            {
                "subject_id": "S1",
                "timestamp": "2026-05-08T02:18:00Z",
                "duration_sec": 120,
                "cell_tower_id": "CT-FAR",
                "call_type": "outgoing",
                "tower_lat": 13.20,
                "tower_lon": 80.10,
            }
        ],
        "gps_context": [
            {
                "subject_id": "S1",
                "timestamp": "2026-05-08T02:18:30Z",
                "lat": 13.05,
                "lon": 80.25,
            }
        ],
    }
    res = client.post("/api/call/analyze", headers=auth(t), json=body)
    assert res.status_code == 200
    out = res.json()
    assert out["counts"]["tower_gps_mismatch"] == 1


# ---------- Ingestion ----------
def test_ingest_and_list_gps(client: TestClient):
    t = _login(client, "analyst@forensic.local")
    case_id = "CASE-2026-0117"
    rows = [
        {
            "subject_id": "S1",
            "timestamp": "2026-05-08T01:39:00Z",
            "latitude": 13.0451,
            "longitude": 80.2567,
            "accuracy_m": 12,
            "source": "phone",
        }
    ]
    res = client.post(f"/api/cases/{case_id}/gps", headers=auth(t), json=rows)
    assert res.status_code == 201
    assert res.json()["inserted"] == 1
    listed = client.get(f"/api/cases/{case_id}/gps", headers=auth(t)).json()
    assert any(r["subject_id"] == "S1" for r in listed)


def test_ingest_unknown_case_404(client: TestClient):
    t = _login(client, "analyst@forensic.local")
    res = client.post("/api/cases/CASE-DOES-NOT-EXIST/gps", headers=auth(t), json=[])
    assert res.status_code == 404


# ---------- Disputes ----------
def test_dispute_lifecycle(client: TestClient):
    t = _login(client, "investigator@forensic.local")
    res = client.post(
        "/api/disputes",
        headers=auth(t),
        json={
            "case_id": "CASE-2026-0117",
            "finding_id": "cause_of_death",
            "reason": "contradicts witness statement at 02:30",
            "module": "autopsy",
        },
    )
    assert res.status_code == 201
    listing = client.get("/api/disputes/CASE-2026-0117", headers=auth(t)).json()
    assert any(d["finding_id"] == "cause_of_death" for d in listing)


def test_dispute_requires_reason(client: TestClient):
    t = _login(client, "investigator@forensic.local")
    res = client.post(
        "/api/disputes",
        headers=auth(t),
        json={"case_id": "CASE-2026-0117", "finding_id": "x", "reason": "  "},
    )
    assert res.status_code == 400


# ---------- Admin ----------
def test_admin_user_lifecycle(client: TestClient):
    t = _login(client, "admin@forensic.local")
    create = client.post(
        "/api/admin/users",
        headers=auth(t),
        json={"email": "newinv@forensic.local", "password": "demo", "role": "INVESTIGATOR", "name": "N. Ew"},
    )
    assert create.status_code == 201
    listed = client.get("/api/admin/users", headers=auth(t)).json()
    assert any(u["email"] == "newinv@forensic.local" for u in listed)

    # Disable then verify they can no longer log in.
    client.post("/api/admin/users/newinv@forensic.local/disable", headers=auth(t))
    fail = client.post("/auth/login", data={"username": "newinv@forensic.local", "password": "demo"})
    assert fail.status_code == 401


def test_non_admin_blocked_from_admin_routes(client: TestClient):
    t = _login(client, "investigator@forensic.local")
    assert client.get("/api/admin/users", headers=auth(t)).status_code == 403


# ---------- Per-investigator scoping ----------
def test_investigator_only_sees_own_cases(client: TestClient):
    inv = _login(client, "investigator@forensic.local")
    # Create a case as investigator — should be visible to that user only.
    cid = "CASE-INV-PRIVATE-001"
    client.post("/api/cases", headers=auth(inv), json={"id": cid, "title": "private"})

    inv_list = client.get("/api/cases", headers=auth(inv)).json()
    assert any(c["id"] == cid for c in inv_list)

    admin = _login(client, "admin@forensic.local")
    client.post(
        "/api/admin/users",
        headers=auth(admin),
        json={"email": "inv2@forensic.local", "password": "demo", "role": "INVESTIGATOR", "name": "I 2"},
    )
    other = _login(client, "inv2@forensic.local")
    other_list = client.get("/api/cases", headers=auth(other)).json()
    assert all(c["id"] != cid for c in other_list)
    # Direct fetch should 404, not 200.
    assert client.get(f"/api/cases/{cid}", headers=auth(other)).status_code == 404


# ---------- PII encryption helper ----------
def test_pii_encryption_roundtrip_no_key(monkeypatch):
    monkeypatch.delenv("FORENSIC_FIELD_KEY", raising=False)
    from storage.encryption import decrypt_field, encrypt_field

    cipher = encrypt_field("Subject A real name")
    assert cipher.startswith("plain:")
    assert decrypt_field(cipher) == "Subject A real name"


def test_pii_encryption_roundtrip_with_key(monkeypatch):
    pytest.importorskip("cryptography")
    import base64
    import secrets as _s

    key = base64.urlsafe_b64encode(_s.token_bytes(32)).decode()
    monkeypatch.setenv("FORENSIC_FIELD_KEY", key)
    from storage.encryption import decrypt_field, encrypt_field

    cipher = encrypt_field("Subject A real name")
    assert cipher.startswith("v1:")
    assert decrypt_field(cipher) == "Subject A real name"
