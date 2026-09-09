from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_anual_returns_one_entry_per_day_of_leap_year() -> None:
    response = client.get(
        "/sol/anual", params={"latitude": -34.6, "longitude": -58.4, "year": 2024}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["latitude"] == -34.6
    assert body["longitude"] == -58.4
    assert body["year"] == 2024
    assert len(body["days"]) == 366  # 2024 es bisiesto
    assert body["days"][0]["date"] == "2024-01-01"
    assert body["days"][-1]["date"] == "2024-12-31"


def test_anual_non_leap_year_has_365_days() -> None:
    response = client.get("/sol/anual", params={"latitude": 0.0, "longitude": 0.0, "year": 2023})
    assert response.status_code == 200
    assert len(response.json()["days"]) == 365


def test_anual_equatorial_day_length_close_to_12_hours() -> None:
    response = client.get("/sol/anual", params={"latitude": 0.0, "longitude": 0.0, "year": 2024})
    assert response.status_code == 200
    for day in response.json()["days"]:
        assert day["day_length_hours"] is not None
        assert 11.9 < day["day_length_hours"] < 12.3
        assert day["always_above"] is None


def test_anual_high_latitude_includes_polar_day_and_night() -> None:
    response = client.get("/sol/anual", params={"latitude": 80.0, "longitude": 0.0, "year": 2024})
    assert response.status_code == 200
    days = response.json()["days"]

    polar_days = [d for d in days if d["sunrise"] is None]
    assert any(d["always_above"] is True for d in polar_days)  # sol de medianoche
    assert any(d["always_above"] is False for d in polar_days)  # noche polar

    normal_days = [d for d in days if d["sunrise"] is not None]
    assert normal_days  # también hay días con orto/ocaso normal
    for day in normal_days:
        assert day["day_length_hours"] is not None
        assert day["always_above"] is None


def test_anual_rejects_out_of_range_latitude() -> None:
    response = client.get("/sol/anual", params={"latitude": 91.0, "longitude": 0.0, "year": 2024})
    assert response.status_code == 422


def test_anual_rejects_out_of_range_longitude() -> None:
    response = client.get("/sol/anual", params={"latitude": 0.0, "longitude": 200.0, "year": 2024})
    assert response.status_code == 422


def test_anual_requires_all_query_params() -> None:
    response = client.get("/sol/anual", params={"latitude": 0.0, "longitude": 0.0})
    assert response.status_code == 422


def test_trayectoria_returns_default_96_samples_covering_the_day() -> None:
    response = client.get(
        "/sol/trayectoria",
        params={"latitude": -34.6, "longitude": -58.4, "date": "2024-06-01"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["latitude"] == -34.6
    assert body["longitude"] == -58.4
    assert body["date"] == "2024-06-01"
    assert len(body["samples"]) == 96
    assert body["samples"][0]["time"] == "2024-06-01T00:00:00Z"
    assert body["samples"][-1]["time"] == "2024-06-01T23:45:00Z"
    for sample in body["samples"]:
        assert -90 <= sample["altitude"] <= 90
        assert 0 <= sample["azimuth"] < 360


def test_trayectoria_respects_custom_num_samples() -> None:
    response = client.get(
        "/sol/trayectoria",
        params={"latitude": 0.0, "longitude": 0.0, "date": "2024-03-20", "num_samples": 24},
    )
    assert response.status_code == 200
    assert len(response.json()["samples"]) == 24


def test_trayectoria_rejects_num_samples_out_of_range() -> None:
    response = client.get(
        "/sol/trayectoria",
        params={"latitude": 0.0, "longitude": 0.0, "date": "2024-03-20", "num_samples": 1000},
    )
    assert response.status_code == 422


def test_trayectoria_rejects_out_of_range_latitude() -> None:
    response = client.get(
        "/sol/trayectoria",
        params={"latitude": 91.0, "longitude": 0.0, "date": "2024-03-20"},
    )
    assert response.status_code == 422


def test_trayectoria_requires_date() -> None:
    response = client.get("/sol/trayectoria", params={"latitude": 0.0, "longitude": 0.0})
    assert response.status_code == 422
