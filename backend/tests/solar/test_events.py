from datetime import UTC, date, datetime, timedelta

import pytest

from app.solar.events import (
    STANDARD_ALTITUDE_SUN,
    _altitude,
    _hour_angle_at_altitude,
    solar_transit,
    sunrise_sunset,
)

# --- Identidades exactas de las funciones auxiliares -----------------------
# El día-largo clásico: cos(H0) = -tan(latitud) * tan(declinación), con
# altitud geométrica (0°, sin refracción/semidiámetro). Independiente de
# cualquier valor numérico de tabla — son identidades trigonométricas.


def test_hour_angle_at_altitude_is_90_at_equator_regardless_of_declination() -> None:
    # En el ecuador el Sol siempre pasa 12h sobre el horizonte y 12h debajo,
    # sea cual sea su declinación (geométricamente, sin refracción).
    for declination_deg in [-23.4, 0.0, 23.4]:
        assert _hour_angle_at_altitude(0.0, declination_deg, 0.0) == pytest.approx(90.0)


def test_hour_angle_at_altitude_borderline_circumpolar() -> None:
    # latitud = declinación: el Sol roza el horizonte a medianoche (H0=180,
    # borde exacto del día polar) — identidad tan(45)*tan(45) = 1.
    assert _hour_angle_at_altitude(45.0, 45.0, 0.0) == pytest.approx(180.0)


def test_hour_angle_at_altitude_borderline_never_rises() -> None:
    # latitud = -declinación: el Sol roza el horizonte a mediodía (H0=0,
    # borde exacto de la noche polar).
    assert _hour_angle_at_altitude(45.0, -45.0, 0.0) == pytest.approx(0.0, abs=1e-4)


def test_hour_angle_at_altitude_none_when_circumpolar_or_never_rises() -> None:
    assert _hour_angle_at_altitude(45.0, 46.0, 0.0) is None  # sol de medianoche
    assert _hour_angle_at_altitude(45.0, -46.0, 0.0) is None  # noche polar


def test_altitude_at_transit_equals_90_minus_zenith_distance() -> None:
    # H=0 (tránsito) con el Sol exactamente en el cenit del observador.
    assert _altitude(45.0, 45.0, 0.0) == pytest.approx(90.0)


def test_altitude_is_zero_six_hours_from_transit_when_declination_is_zero() -> None:
    # H=90° con declinación 0: el Sol está justo en el horizonte,
    # independientemente de la latitud.
    for latitude_deg in [-60.0, 0.0, 60.0]:
        assert _altitude(latitude_deg, 0.0, 90.0) == pytest.approx(0.0, abs=1e-9)


# --- Comportamiento integrado (tránsito, orto/ocaso) ------------------------


@pytest.mark.parametrize(
    "day",
    [date(2024, 1, 15), date(2024, 4, 15), date(2024, 7, 15), date(2024, 10, 15)],
)
def test_transit_at_greenwich_within_equation_of_time_bound(day: date) -> None:
    # En longitud 0°, el mediodía solar difiere del mediodía UT por la
    # ecuación del tiempo, que nunca supera ~16-17 minutos en todo el año.
    transit = solar_transit(day, longitude_deg=0.0)
    noon = datetime(day.year, day.month, day.day, 12, 0, 0, tzinfo=UTC)
    assert abs((transit - noon).total_seconds()) < 20 * 60


@pytest.mark.parametrize(
    "day",
    [date(2024, 1, 15), date(2024, 4, 15), date(2024, 7, 15), date(2024, 10, 15)],
)
def test_equatorial_day_length_close_to_12_hours(day: date) -> None:
    # En el ecuador el día dura ~12h todo el año (una pequeña diferencia
    # constante por la refracción/semidiámetro de STANDARD_ALTITUDE_SUN).
    result = sunrise_sunset(day, latitude_deg=0.0, longitude_deg=0.0)
    assert result.sunrise is not None
    assert result.sunset is not None
    day_length = result.sunset - result.sunrise
    assert timedelta(hours=11, minutes=55) < day_length < timedelta(hours=12, minutes=15)


def test_sunrise_transit_sunset_are_in_order() -> None:
    # Buenos Aires, en un día cualquiera sin casos límite (polares).
    result = sunrise_sunset(date(2024, 6, 1), latitude_deg=-34.6, longitude_deg=-58.4)
    assert result.sunrise is not None
    assert result.sunset is not None
    assert result.sunrise < result.transit < result.sunset


def test_midnight_sun_near_june_solstice_at_high_latitude() -> None:
    result = sunrise_sunset(date(2024, 6, 21), latitude_deg=80.0, longitude_deg=0.0)
    assert result.sunrise is None
    assert result.sunset is None
    assert result.always_above is True


def test_polar_night_near_december_solstice_at_high_latitude() -> None:
    result = sunrise_sunset(date(2024, 12, 21), latitude_deg=80.0, longitude_deg=0.0)
    assert result.sunrise is None
    assert result.sunset is None
    assert result.always_above is False


def test_default_altitude_is_standard_altitude_sun() -> None:
    day, lat, lon = date(2024, 6, 1), -34.6, -58.4
    assert sunrise_sunset(day, lat, lon) == sunrise_sunset(day, lat, lon, STANDARD_ALTITUDE_SUN)
