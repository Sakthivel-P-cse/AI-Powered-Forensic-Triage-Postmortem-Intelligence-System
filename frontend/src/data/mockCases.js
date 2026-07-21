// Mock case dataset. Mirrors the FIPL output schemas in the spec.
// Two cases: one CRITICAL (impossible-travel contradiction), one MEDIUM.

export const mockCases = [
  {
    id: 'CASE-2026-0117',
    title: 'Riverside Apartments — Suspicious Death',
    status: 'IN_TRIAGE',
    risk: {
      score: 84,
      level: 'CRITICAL',
      factors: [
        { name: 'Timeline gaps (CCTV)', value: 12, max: 20, note: '23-min blackout 02:14–02:37' },
        { name: 'Contradiction severity', value: 25, max: 25, note: '1 IMPOSSIBLE travel contradiction' },
        { name: 'GPS / call inconsistency', value: 15, max: 20, note: 'Cell tower vs GPS mismatch at 02:18' },
        { name: 'Autopsy / scene inconsistency', value: 20, max: 20, note: 'TOD window contradicts subject alibi' },
        { name: 'Behavioral anomalies', value: 12, max: 15, note: 'Re-entry + loitering at scene' },
      ],
      briefing:
        'Cross-source analysis reveals one IMPOSSIBLE-travel contradiction between GPS ping at 02:18 (Riverside lot) and CCTV log at 02:24 (Building A north entrance, 11.4 km). Autopsy postmortem indicators (rigor onset, livor blanchable) place TOD window 03:00–06:30, which conflicts with the subject\'s stated departure at 01:50. AI-assisted finding — analyst review required.',
      next_steps: [
        'Subpoena cell-tower data for window 01:30–03:30',
        'Re-interview subject regarding 02:14–02:37 CCTV blackout',
        'Confirm vehicle GPS chain-of-custody for unit VHL-7732',
      ],
      caveats: [
        'GPS accuracy at 02:18 reported 38 m — within tolerance.',
        'CCTV camera CAM-04 had a firmware reboot 02:09; verify clock sync.',
      ],
    },
    subject: { case_subject_id: 'S-001', label: 'Subject A' },
    created_at: '2026-05-08T19:42:00Z',
    analyst_id: null,
    autopsy: {
      cause_of_death: { value: 'Blunt force trauma to the parietal region', confidence: 0.82 },
      manner_of_death: { value: 'Undetermined (pending investigation)', confidence: 0.55 },
      injuries: [
        { description: 'Linear laceration, 4.2 cm', location: 'Right parietal scalp', severity: 'Severe' },
        { description: 'Contusion, ovoid', location: 'Left lateral neck', severity: 'Moderate' },
        { description: 'Defensive abrasions', location: 'Bilateral forearms', severity: 'Mild' },
      ],
      toxicology: [
        { substance: 'Ethanol', level: '0.06% w/v', significance: 'Below local impairment threshold' },
        { substance: 'Diphenhydramine', level: '0.18 µg/mL', significance: 'Therapeutic range' },
      ],
      weapon_indicators: ['Blunt object with rounded edge consistent with metal pipe (≥3 cm diameter)'],
      postmortem_indicators: {
        rigor_mortis: 'Onset — jaw and neck',
        livor_mortis: 'Blanchable, posterior dependent',
        body_temp_celsius: 32.1,
      },
      tod_estimate: {
        indicator_window_hours: [4, 8],
        corrected_window_hours: [3.5, 7.0],
        confidence: 'MEDIUM',
        reasoning:
          'Algor mortis (Δ = 4.9°C, ambient 19°C, light clothing) → ~5.9h. Rigor onset narrows ≥2h. Blanchable livor caps ≤8h. Combined window 3.5–7.0h before examination at 09:12.',
        caveats: ['Ambient temperature variance ±1.5°C overnight', 'Body weight not yet confirmed'],
      },
      key_observations: [
        'Defensive injuries indicate awareness prior to fatal blow',
        'No ligature marks',
        'Petechiae absent — asphyxiation unlikely as sole mechanism',
      ],
      conflicts_in_report: [
        'Examiner notes "minimal blood at scene" — inconsistent with severity of parietal laceration; secondary scene possible.',
      ],
      summary:
        'Findings consistent with blunt-force homicide. Postmortem window places death between 02:42 and 06:12 local time. Possible body movement post-mortem.',
      overall_confidence: 0.74,
      reasoning_chain: [
        'Parietal laceration depth + bone involvement → blunt force, severe.',
        'Defensive abrasions on forearms → conscious resistance.',
        'Blood volume at scene insufficient for laceration severity → potential post-mortem transport.',
        'Combined indicator window narrows TOD to 3.5–7.0h pre-examination.',
      ],
    },
    cctv: {
      sorted_events: [
        { id: 'e1', camera_id: 'CAM-01', location: 'Lobby', timestamp: '2026-05-08T01:42:10Z', event_type: 'person_entered', attributes: { count: 1, direction: 'inbound' } },
        { id: 'e2', camera_id: 'CAM-04', location: 'Bldg A — North entrance', timestamp: '2026-05-08T01:48:55Z', event_type: 'person_entered', attributes: { direction: 'inbound' } },
        { id: 'e3', camera_id: 'CAM-04', location: 'Bldg A — North entrance', timestamp: '2026-05-08T02:09:02Z', event_type: 'camera_offline', attributes: { reason: 'firmware_reboot' } },
        { id: 'e4', camera_id: 'CAM-04', location: 'Bldg A — North entrance', timestamp: '2026-05-08T02:24:18Z', event_type: 'person_exited', attributes: { direction: 'outbound' } },
        { id: 'e5', camera_id: 'CAM-07', location: 'Parking — east deck', timestamp: '2026-05-08T02:31:44Z', event_type: 'vehicle_started', attributes: { plate_partial: 'TN-** **23' } },
        { id: 'e6', camera_id: 'CAM-04', location: 'Bldg A — North entrance', timestamp: '2026-05-08T02:53:11Z', event_type: 'person_entered', attributes: { direction: 'inbound' } },
        { id: 'e7', camera_id: 'CAM-01', location: 'Lobby', timestamp: '2026-05-08T03:11:09Z', event_type: 'person_exited', attributes: { direction: 'outbound' } },
      ],
      gaps: [
        { start: '2026-05-08T02:09:02Z', end: '2026-05-08T02:24:18Z', duration_min: 15.3, flag_reason: 'Camera offline window during key timeframe' },
      ],
      anomalies: [
        { description: 'Re-entry pattern at CAM-04 within 29 minutes of exit', severity: 'HIGH' },
        { description: 'Loitering at CAM-04 north entrance prior to camera reboot', severity: 'MEDIUM' },
      ],
      movement_summary:
        'Subject A enters lobby 01:42, reaches Bldg A north entrance 01:49, then a 15-minute camera-offline gap. Subject exits at 02:24, vehicle activity at 02:32, returns 02:53 and finally exits the lobby at 03:11.',
      risk_flags: ['CCTV blackout overlaps GPS contradiction window'],
      reasoning_chain: [
        'Entry at 01:48 followed by 15-min CAM-04 offline → coverage hole.',
        'Re-entry 02:53 after vehicle activity 02:31 → possible round trip.',
        'Final exit 03:11 with no further re-entry.',
      ],
    },
    gps: [
      { id: 'g1', timestamp: '2026-05-08T01:39:00Z', lat: 13.0451, lng: 80.2567, accuracy_m: 12, source: 'phone' },
      { id: 'g2', timestamp: '2026-05-08T01:50:00Z', lat: 13.0488, lng: 80.2521, accuracy_m: 14, source: 'phone' },
      { id: 'g3', timestamp: '2026-05-08T02:18:00Z', lat: 13.1010, lng: 80.1620, accuracy_m: 38, source: 'phone' },
      { id: 'g4', timestamp: '2026-05-08T02:31:00Z', lat: 13.0497, lng: 80.2515, accuracy_m: 18, source: 'vehicle' },
      { id: 'g5', timestamp: '2026-05-08T03:14:00Z', lat: 13.0445, lng: 80.2570, accuracy_m: 11, source: 'phone' },
    ],
    correlation: {
      unified_timeline: [
        { ts: '2026-05-08T01:39:00Z', source: 'GPS', label: 'Phone @ home (13.0451, 80.2567)' },
        { ts: '2026-05-08T01:42:10Z', source: 'CCTV', label: 'CAM-01 lobby — entered' },
        { ts: '2026-05-08T01:48:55Z', source: 'CCTV', label: 'CAM-04 north — entered' },
        { ts: '2026-05-08T01:50:00Z', source: 'GPS', label: 'Phone (13.0488, 80.2521)' },
        { ts: '2026-05-08T02:09:02Z', source: 'CCTV', label: 'CAM-04 — OFFLINE' },
        { ts: '2026-05-08T02:18:00Z', source: 'GPS', label: 'Phone (13.0902, 80.1751) — 11.4 km away' },
        { ts: '2026-05-08T02:24:18Z', source: 'CCTV', label: 'CAM-04 — exited' },
        { ts: '2026-05-08T02:31:00Z', source: 'GPS', label: 'Vehicle (13.0497, 80.2515)' },
        { ts: '2026-05-08T02:53:11Z', source: 'CCTV', label: 'CAM-04 — re-entered' },
        { ts: '2026-05-08T03:14:00Z', source: 'GPS', label: 'Phone @ home' },
      ],
      contradictions: [
        {
          id: 'c1',
          type: 'IMPOSSIBLE',
          source_a: { kind: 'GPS', ts: '2026-05-08T02:18:00Z', loc: '(13.0902, 80.1751)' },
          source_b: { kind: 'CCTV', ts: '2026-05-08T02:24:18Z', loc: 'CAM-04 north entrance' },
          time_delta_min: 6.3,
          distance_km: 11.4,
          explanation:
            'Phone GPS places subject 11.4 km from CAM-04 only 6 minutes before CCTV records the same subject exiting Bldg A. Minimum drive time at 60 km/h ≈ 11 minutes. Travel mathematically impossible.',
          investigative_priority: 'CRITICAL',
        },
        {
          id: 'c2',
          type: 'SUSPICIOUS',
          source_a: { kind: 'CCTV', ts: '2026-05-08T02:31:44Z', loc: 'CAM-07 east deck' },
          source_b: { kind: 'GPS', ts: '2026-05-08T02:31:00Z', loc: 'Vehicle near Bldg A' },
          time_delta_min: 0.7,
          distance_km: 0.2,
          explanation:
            'Vehicle GPS and CAM-07 vehicle-start event are temporally consistent. Flagged SUSPICIOUS only because phone GPS at 02:18 is incompatible with this trajectory.',
          investigative_priority: 'MEDIUM',
        },
      ],
      evidence_links: ['autopsy:CASE-2026-0117', 'cctv:CAM-04', 'gps:phone-S001'],
      inconsistency_summary:
        '1 IMPOSSIBLE and 1 SUSPICIOUS contradiction across 3 sources. Highest-priority lead: phone GPS at 02:18 vs CAM-04 at 02:24.',
    },
  },
  {
    id: 'CASE-2026-0118',
    title: 'Marina Promenade — Found Deceased',
    status: 'INTAKE',
    risk: {
      score: 42,
      level: 'MEDIUM',
      factors: [
        { name: 'Timeline gaps (CCTV)', value: 12, max: 20, note: '38-min gap before discovery' },
        { name: 'Contradiction severity', value: 5, max: 25, note: '1 UNVERIFIABLE movement' },
        { name: 'GPS / call inconsistency', value: 10, max: 20, note: 'Missing GPS during key window' },
        { name: 'Autopsy / scene inconsistency', value: 10, max: 20, note: 'Partial conflict on TOD' },
        { name: 'Behavioral anomalies', value: 5, max: 15, note: 'Re-entry pattern only' },
      ],
      briefing:
        'No impossible-travel contradictions detected. One UNVERIFIABLE movement between CAM-12 and CAM-15 (no inter-camera distance configured). Postmortem indicators broadly consistent with reported timeline. AI-assisted finding — analyst review required.',
      next_steps: ['Add inter-camera distance map for promenade', 'Request carrier records for window 22:00–23:00'],
      caveats: ['Subject phone reported powered off at 22:14'],
    },
    subject: { case_subject_id: 'S-002', label: 'Subject B' },
    created_at: '2026-05-09T06:11:00Z',
    analyst_id: 'analyst@forensic.local',
    autopsy: null,
    cctv: { sorted_events: [], gaps: [], anomalies: [], movement_summary: '', risk_flags: [], reasoning_chain: [] },
    gps: [],
    correlation: { unified_timeline: [], contradictions: [], evidence_links: [], inconsistency_summary: 'No critical contradictions.' },
  },
];
