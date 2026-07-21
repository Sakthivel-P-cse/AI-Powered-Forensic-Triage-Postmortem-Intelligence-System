from modules.risk.scorer import RiskInput, level_for_score, score_case


def test_level_thresholds():
    assert level_for_score(0) == "LOW"
    assert level_for_score(30) == "LOW"
    assert level_for_score(31) == "MEDIUM"
    assert level_for_score(60) == "MEDIUM"
    assert level_for_score(61) == "HIGH"
    assert level_for_score(80) == "HIGH"
    assert level_for_score(81) == "CRITICAL"
    assert level_for_score(100) == "CRITICAL"


def test_factor_caps_respected():
    inp = RiskInput(
        longest_cctv_gap_min=240,            # cap 20
        impossible_contradictions=5,          # capped at 25
        suspicious_contradictions=5,          # ignored when impossible already saturates
        unverifiable_contradictions=10,       # contributes within the 25 cap
        cell_tower_gps_mismatch=True,
        missing_gps_in_key_window=True,
        tod_contradicts_alibi=True,
        re_entry_pattern=True,
        loitering_at_scene=True,
        unusual_movement_speed=True,
    )
    score, level, factors = score_case(inp)
    by_name = {f.name: f for f in factors}
    assert by_name["Timeline gaps (CCTV)"].value == 20
    assert by_name["Contradiction severity"].value == 25
    assert by_name["GPS / call inconsistency"].value == 20
    assert by_name["Autopsy / scene inconsistency"].value == 20
    assert by_name["Behavioral anomalies"].value == 15
    assert score == 100
    assert level == "CRITICAL"


def test_clean_case_low_risk():
    score, level, _ = score_case(RiskInput())
    assert score == 0
    assert level == "LOW"


def test_partial_autopsy_conflict_does_not_stack_with_full():
    """Spec: TOD vs alibi (20) wins; partial conflict alone is 10."""
    full = score_case(RiskInput(tod_contradicts_alibi=True))[0]
    partial = score_case(RiskInput(partial_autopsy_conflict=True))[0]
    assert full == 20
    assert partial == 10
