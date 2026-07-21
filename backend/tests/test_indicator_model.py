from modules.tod.indicator_model import IndicatorInput, estimate_window


def test_no_inputs_returns_widest_window():
    w = estimate_window(IndicatorInput())
    assert w.indicator_window_hours == (0.0, 48.0)


def test_rigor_only_yields_table_window():
    w = estimate_window(IndicatorInput(rigor="onset"))
    assert w.indicator_window_hours == (2.0, 6.0)


def test_combined_indicators_intersect():
    """rigor onset (2–6) ∩ livor blanchable (2–8) → (2,6)."""
    w = estimate_window(IndicatorInput(rigor="onset", livor="blanchable"))
    assert w.indicator_window_hours == (2.0, 6.0)


def test_algor_modifier_widens_for_no_clothing():
    bare = estimate_window(IndicatorInput(body_temp_c=32.1, ambient_temp_c=21, clothing="none"))
    light = estimate_window(IndicatorInput(body_temp_c=32.1, ambient_temp_c=21, clothing="light"))
    # Bare body: cooling correction +10% so the centre of the algor window shifts later.
    assert bare.indicator_window_hours[1] >= light.indicator_window_hours[1]


def test_corrected_window_within_one_hour_of_indicator():
    w = estimate_window(
        IndicatorInput(body_temp_c=32.1, ambient_temp_c=19, body_weight_kg=76, clothing="light",
                       rigor="onset", livor="blanchable")
    )
    lo, hi = w.indicator_window_hours
    clo, chi = w.corrected_window_hours
    assert lo - 1.0 <= clo <= hi + 1.0
    assert lo - 1.0 <= chi <= hi + 1.0
