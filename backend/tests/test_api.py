"""End-to-end smoke through FastAPI TestClient.

No live Gemini key — the client returns the deterministic stub, so AI fields
are empty/short, but deterministic outputs must still be present and correct.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def analyst_token(client: TestClient) -> str:
    res = client.post(
        "/auth/login",
        data={"username": "analyst@forensic.local", "password": "demo"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def auth(t: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {t}"}


def test_login_and_me(client: TestClient, analyst_token: str):
    me = client.get("/auth/me", headers=auth(analyst_token))
    assert me.status_code == 200
    assert me.json()["role"] == "ANALYST"


def test_unauthenticated_blocked(client: TestClient):
    res = client.get("/api/cases")
    assert res.status_code == 401


def test_cases_seed_visible(client: TestClient, analyst_token: str):
    res = client.get("/api/cases", headers=auth(analyst_token))
    assert res.status_code == 200
    ids = {c["id"] for c in res.json()}
    assert "CASE-2026-0117" in ids


def test_correlation_endpoint_flags_impossible(client: TestClient, analyst_token: str):
    body = {
        "events": [
            {
                "source": "GPS",
                "subject_id": "S1",
                "timestamp": "2026-05-08T02:18:00Z",
                "lat": 13.1010,
                "lon": 80.1620,
            },
            {
                "source": "CCTV",
                "subject_id": "S1",
                "timestamp": "2026-05-08T02:24:18Z",
                "lat": 13.0488,
                "lon": 80.2521,
            },
        ]
    }
    res = client.post("/api/correlation/detect", headers=auth(analyst_token), json=body)
    assert res.status_code == 200
    out = res.json()
    types = [c["type"] for c in out["contradictions"]]
    assert "IMPOSSIBLE" in types
    assert any(c["investigative_priority"] == "CRITICAL" for c in out["contradictions"])


def test_risk_endpoint_returns_authoritative_score(client: TestClient, analyst_token: str):
    res = client.post(
        "/api/risk/score",
        headers=auth(analyst_token),
        json={
            "longest_cctv_gap_min": 15.3,
            "impossible_contradictions": 1,
            "cell_tower_gps_mismatch": True,
            "tod_contradicts_alibi": True,
            "re_entry_pattern": True,
            "loitering_at_scene": True,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["risk_score"] == 79
    assert body["risk_level"] == "HIGH"
    assert len(body["factor_breakdown"]) == 5


def test_signoff_immutable(client: TestClient, analyst_token: str):
    case_id = "CASE-2026-0117"
    a = client.post(f"/api/signoff/{case_id}", headers=auth(analyst_token), json={"disputed_findings": []})
    assert a.status_code == 201
    first = a.json()
    b = client.post(f"/api/signoff/{case_id}", headers=auth(analyst_token), json={"disputed_findings": ["x"]})
    # Spec: signatures are immutable. Same record must come back.
    assert b.status_code == 201
    assert b.json()["signed_at"] == first["signed_at"]
    assert b.json()["disputed_findings"] == first["disputed_findings"]


def test_investigator_cannot_sign(client: TestClient):
    inv = TestClient(app).post(
        "/auth/login",
        data={"username": "investigator@forensic.local", "password": "demo"},
    ).json()["access_token"]
    res = TestClient(app).post(
        "/api/signoff/CASE-2026-0118",
        headers=auth(inv),
        json={"disputed_findings": []},
    )
    assert res.status_code == 403
