# AI-Powered Forensic Triage & Postmortem Intelligence System

> Deterministic engines compute. AI explains. Humans decide.

A forensic intelligence platform that fuses autopsy reports, CCTV logs,
GPS pings and call records to detect cross-source contradictions, refine
time-of-death estimates, and generate auditable triage briefings — every
inference reviewable, every export gated by a Forensic Analyst signature.

---

## Repository layout

```
hackathon/
├── frontend/          Vite + React + Tailwind UI (dark forensic theme)
├── backend/           FastAPI service (modules + FIPL + deterministic engines)
├── sample_data/       Autopsy text, CCTV CSV, GPS + call JSON
├── Dockerfile.backend
├── Dockerfile.frontend
└── docker-compose.yml
```

## Architecture overview

| Layer | Responsibility | Files |
|------|----------------|-------|
| **L1 — Deterministic** | Math, no AI. Haversine, travel-time logic, postmortem indicator tables, weighted risk scorer, OCR. | `backend/modules/correlation/contradiction_engine.py`, `modules/risk/scorer.py`, `modules/tod/indicator_model.py` |
| **L2 — FIPL prompts** | Domain-constrained prompt templates with mandatory schema, reasoning chain, uncertainty rules, scope limits. | `backend/ai/fipl/*` |
| **L3 — Orchestration** | Routing, RBAC, caching, sign-off gate, audit. | `backend/main.py`, `auth/`, `ai/cache.py` |
| **L4 — UI** | Investigation dashboard, contradiction matrix, timeline, map, risk gauge, dispute & sign-off. | `frontend/src/**` |

### The three forensic-domain contributions

1. **Cross-source temporal contradiction detection** — `contradiction_engine.py` flags pairs of events from different sources for the same subject as IMPOSSIBLE / SUSPICIOUS / UNVERIFIABLE based on Haversine distance and minimum travel time per transport mode.
2. **Structured postmortem indicator model** — `indicator_model.py` maps rigor / livor / algor mortis to time windows deterministically before Gemini ever sees the data. Gemini only refines with scene context.
3. **Forensic Intelligence Prompt Layer (FIPL)** — every prompt opens with a forensic role assignment and closes with a scope limitation; mandates JSON output, reasoning chain, uncertainty flags, and explicit conflict reporting. See `backend/ai/fipl/_base.py`.

## Setup

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
# → http://localhost:5173
```

The UI ships with mock data (`src/data/mockCases.js`) so it runs without a backend. Demo logins:

| Email | Password | Role |
|---|---|---|
| `investigator@forensic.local` | `demo` | INVESTIGATOR |
| `analyst@forensic.local` | `demo` | ANALYST |
| `admin@forensic.local` | `demo` | ADMIN |

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optional: set GEMINI_API_KEY, SUPABASE_*, FIREBASE_* for live mode
uvicorn main:app --reload
# → http://localhost:8000/docs
```

Without `GEMINI_API_KEY` the client returns a deterministic stub response, so endpoints remain callable for demos.

### Database

```bash
psql "$SUPABASE_DB_URL" -f backend/db/schema.sql
```

### Docker

```bash
docker compose up --build
```

## API surface (skeleton)

| Method | Path | Roles | Purpose |
|---|---|---|---|
| POST | `/auth/login` | any | OAuth2 password flow → JWT |
| GET  | `/auth/me`    | authed | Current user |
| GET  | `/api/cases` | authed | List all cases |
| POST | `/api/cases` | INV / ANL / ADM | Create case |
| GET  | `/api/cases/{id}` | authed | Fetch case |
| PATCH| `/api/cases/{id}` | ANL / ADM | Update case |
| POST | `/api/evidence/upload` | INV / ANL / ADM | Multipart upload → OCR → autopsy chain |
| POST | `/api/autopsy/analyze` | INV / ANL / ADM | Text → FIPL → Gemini |
| POST | `/api/cctv/analyze` | INV / ANL / ADM | Sort + gap-flag → FIPL → Gemini |
| POST | `/api/call/analyze` | INV / ANL / ADM | Tower↔GPS mismatch + active-call-during-movement flags |
| POST | `/api/correlation/detect` | INV / ANL / ADM | Deterministic matrix + FIPL explanations |
| POST | `/api/risk/score` | INV / ANL / ADM | Deterministic weighted score + FIPL briefing |
| POST | `/api/tod/estimate` | INV / ANL / ADM | Indicator window + FIPL refinement |
| POST/GET | `/api/cases/{id}/cctv` | INV / ANL / ADM | Bulk-ingest or list CCTV rows |
| POST/GET | `/api/cases/{id}/gps` | INV / ANL / ADM | Bulk-ingest or list GPS pings |
| POST/GET | `/api/cases/{id}/calls` | INV / ANL / ADM | Bulk-ingest or list call records |
| POST | `/api/disputes` | authed | File a per-finding dispute against a deterministic or AI output |
| GET  | `/api/disputes/{case_id}` | authed | List disputes on a case |
| GET  | `/api/signoff/{id}` | authed | Read sign-off state |
| POST | `/api/signoff/{id}` | ANL / ADM | Sign report (immutable) |
| GET  | `/api/admin/users` | ADM | List users |
| POST | `/api/admin/users` | ADM | Create user (INVESTIGATOR / ANALYST / ADMIN) |
| POST | `/api/admin/users/{email}/{disable\|enable}` | ADM | Toggle account |
| GET  | `/api/audit/recent` | ADM | Tail of in-memory audit ring |

## Seeding the demo case

```bash
cd backend
python scripts/seed.py
# → [seed] case=CASE-2026-0117 cctv=N gps=N calls=N
```

Loads `sample_data/cctv_log.csv`, `gps_log.json`, `call_log.json` into the
in-memory repos (or Supabase, if configured) under case `CASE-2026-0117`.
Re-running appends; for a clean slate, restart the backend.

## Tests

```bash
cd backend
pytest -q
```

34 deterministic + integration tests cover Haversine, contradiction ladder,
risk weight caps, indicator-window intersection, JWT/RBAC, immutable sign-off,
call-log analyzer, ingestion endpoints, dispute API, admin user management,
per-investigator scoping, and field-level encryption roundtrip.

Swagger UI at `/docs`.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `JWT_SECRET` | HMAC key for access tokens | dev fallback |
| `GEMINI_API_KEY` | Gemini live mode (omit → deterministic stub) | unset |
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Supabase persistence (omit → in-memory) | unset |
| `FORENSIC_FIELD_KEY` | 32-byte url-safe-base64 AES-256-GCM key for PII fields (omit → `plain:` prefix passthrough) | unset |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |

## Ethical & legal guarantees (enforced in code)

1. **AES-256 at-rest** — Firebase Storage default; field-level encryption for subject PII.
2. **Role-scoped data access** — `auth/rbac.py`; only ADMIN crosses cases.
3. **Human sign-off gate** — `report_signoffs` table + `SignOffGate.jsx`; reports lock in DRAFT until ANALYST signs.
4. **Explainability** — every Gemini call returns `reasoning_chain[]`; `AIOutputCard.jsx` always renders it.
5. **Audit logging** — `audit_logs` table; every inference, upload, and signature recorded.
6. **Data minimisation** — only analysis-relevant text reaches Gemini; subjects referenced by internal ID only.

## Future scope

Federated learning across agencies, multilingual FIPL templates (Tamil/Hindi/Arabic), real-time IoT sensor ingestion, cross-case pattern recognition via pgvector, predictive triage classifier.
