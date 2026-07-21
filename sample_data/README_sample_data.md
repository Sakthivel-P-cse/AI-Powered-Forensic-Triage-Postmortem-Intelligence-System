# Sample Data — CR-2024-00471
## AIVENTRA Forensic Triage System Test Case

---

## Case Narrative (for internal testing only)

SUBJ-001 (victim) is found deceased in Flat 4B, Block B, Residential Complex A
on 2024-11-02 at 07:22 by a maintenance worker (SUBJ-003).

SUBJ-002 (person of interest) visited the same floor between 20:12 and 22:47
on 2024-11-01 — fully within the estimated time-of-death window.

The sample data is deliberately constructed with:
- 2 CRITICAL contradictions (designed to trigger max risk scoring)
- 2 SUSPICIOUS contradictions (travel time anomalies)
- One subject whose phone goes completely dark at the onset of the ToD window
- A consistent cross-source corroboration trail to validate fusion layer output

---

## Files and Their Module Targets

| File | Feeds Into | Format |
|------|-----------|--------|
| autopsy_report.txt | Module 2 — Autopsy Report Analysis | Plain text (simulates OCR output) |
| cctv_logs.json | Module 3 — CCTV Log Analysis | JSON array (matches module input schema) |
| gps_logs.json | Module 4 — Contradiction Engine | JSON array |
| call_logs.json | Module 4 — Contradiction Engine | JSON array |
| scene_conditions.json | Module TOD — ToD Estimator | JSON object |
| contradiction_matrix_expected.json | Validation — expected engine output | JSON (ground truth) |
| risk_score_expected.json | Validation — expected scorer output | JSON (ground truth) |

---

## Key Test Assertions

When you run the full pipeline against this dataset, your system should produce:

### Contradiction Engine
- CONT-001: SUSPICIOUS (CAM-01 exit → CAM-05, 21 min, 2.1 km, walking impossible)
- CONT-002: SUSPICIOUS (CAM-01 exit → CALL-005 tower, 5 min, cell handoff ambiguous)
- CONT-003: CRITICAL flag (SUBJ-001 phone dark at 20:08, onset of ToD window)
- CONT-004: CRITICAL flag (SUBJ-002 on Floor 4 at 20:10, 2 min after phone dark)

### ToD Estimator
- Algor mortis raw estimate: ~10.24h before exam (2024-11-03 09:15)
  → Raw window: ~2024-11-02 23:00 ± 1h
- Rigor correction: full rigor → 6–12h → consistent
- Livor correction: fixed lividity → 12h+ → lower bound: 2024-11-01 ~20:00
- Final corrected window: 2024-11-01 20:00 – 23:30
- Confidence: MEDIUM

### Risk Scorer
- Expected score: 95 / 100
- Expected level: CRITICAL
- All five factor buckets should contribute points

### Fusion Layer
- suspicion_score should be ≥ 0.90
- triage_priority: CRITICAL
- key_leads should include the 20:08–20:12 temporal convergence as lead #1

---

## Haversine Check (for contradiction_engine.py unit test)

Location A: Residential Complex A gate → lat 13.0614, lon 80.2502
Location B: MG Road petrol station    → lat 13.0729, lon 80.2603

Expected Haversine distance: ~2.07–2.15 km
Walking time @ 5 km/h: ~24.8–25.8 min
Time delta in data: 21 min → SUSPICIOUS (< min_walk_time × 1.0, > min_drive_time)

Use this as a unit test for your haversine.py module.

---

## Notes on Synthetic Data

- Subject names replaced with SUBJ-001/002/003 — matches data minimization requirement
- Camera IDs, tower IDs, GPS coords are fictionalised but geographically consistent
  within Chennai grid (lat ~13.05–13.07, lon ~80.24–80.26)
- Timestamps are internally consistent and designed to produce deterministic outputs
- The `flag` fields in GPS and call log entries are annotation comments for developers
  — strip these before sending to Gemini (data minimization rule)
