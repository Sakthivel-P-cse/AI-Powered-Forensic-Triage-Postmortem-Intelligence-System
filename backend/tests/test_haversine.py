from modules.correlation.haversine import haversine_km


def test_zero_distance():
    assert haversine_km(13.0, 80.0, 13.0, 80.0) == 0.0


def test_known_pair_chennai():
    # ~11.35 km between two Chennai-area points; verify within ±0.1 km.
    d = haversine_km(13.1010, 80.1620, 13.0488, 80.2521)
    assert 11.2 <= d <= 11.5


def test_symmetric():
    a = haversine_km(10.0, 20.0, 30.0, 40.0)
    b = haversine_km(30.0, 40.0, 10.0, 20.0)
    assert abs(a - b) < 1e-9
