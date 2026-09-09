from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.solar.time import (
    J2000,
    datetime_from_julian_day,
    julian_century,
    julian_day,
    mean_sidereal_time,
)

J2000_MOMENT = datetime(2000, 1, 1, 12, 0, 0)


def test_j2000_epoch() -> None:
    assert julian_day(J2000_MOMENT) == pytest.approx(2_451_545.0)


def test_unix_epoch() -> None:
    assert julian_day(datetime(1970, 1, 1, 0, 0, 0)) == pytest.approx(2_440_587.5)


def test_naive_datetime_assumed_utc() -> None:
    naive = datetime(2024, 6, 15, 18, 30)
    aware = naive.replace(tzinfo=UTC)
    assert julian_day(naive) == julian_day(aware)


def test_timezone_aware_input_converted_to_utc() -> None:
    # 09:00 en Buenos Aires (UTC-3) == 12:00 UT == J2000.0
    local = datetime(2000, 1, 1, 9, 0, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    assert julian_day(local) == pytest.approx(2_451_545.0)


@pytest.mark.parametrize(
    "delta",
    [
        timedelta(seconds=1),
        timedelta(hours=6),
        timedelta(days=1),
        timedelta(days=-1),
        timedelta(days=90),  # cruza fin de mes/trimestre
        timedelta(days=-400),  # cruza fin de año hacia atrás
        timedelta(days=10_000),  # ~27 años, cruza varios bisiestos
    ],
)
def test_matches_calendar_arithmetic(delta: timedelta) -> None:
    """El JD debe avanzar exactamente lo mismo que el calendario gregoriano
    proléptico de `datetime`, sin importar que la ventana cruce meses, años
    o siglos bisiestos.

    Tolerancia absoluta (no la relativa por default de `approx`): un JD
    ronda 2.45 millones, así que restar dos JD casi iguales en float64
    cancela los dígitos altos y deja ~1e-8 días (~1 ms) de piso de
    precisión — muy por debajo de lo que necesita esta app (la precisión
    del método de Meeus usado en `coordinates.py` es del orden de minutos).
    """
    expected_diff = delta.total_seconds() / 86_400
    actual_diff = julian_day(J2000_MOMENT + delta) - julian_day(J2000_MOMENT)
    assert actual_diff == pytest.approx(expected_diff, abs=1e-8)


def test_julian_century_at_epoch() -> None:
    assert julian_century(J2000) == pytest.approx(0.0)


@pytest.mark.parametrize("centuries", [1, -1, 2.5])
def test_julian_century_scales_linearly(centuries: float) -> None:
    jd = J2000 + centuries * 36_525.0
    assert julian_century(jd) == pytest.approx(centuries)


def test_datetime_from_julian_day_at_j2000_epoch() -> None:
    assert datetime_from_julian_day(J2000) == J2000_MOMENT.replace(tzinfo=UTC)


@pytest.mark.parametrize(
    "moment",
    [
        datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        datetime(1992, 10, 13, 0, 0, 0, tzinfo=UTC),
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
        datetime(2024, 2, 29, 18, 30, 15, tzinfo=UTC),  # 29 de febrero bisiesto
        datetime(1, 3, 1, 0, 0, 0, tzinfo=UTC),  # año 1, cruza el ajuste gregoriano
        datetime(9999, 12, 31, 23, 59, 59, tzinfo=UTC),  # extremo del rango de datetime
    ],
)
def test_datetime_from_julian_day_is_inverse_of_julian_day(moment: datetime) -> None:
    assert datetime_from_julian_day(julian_day(moment)) == moment


def test_mean_sidereal_time_matches_meeus_example_12a() -> None:
    # Meeus, Astronomical Algorithms cap. 12, ejemplo 12.a: 1987 abril 10.0 UT.
    jd = julian_day(datetime(1987, 4, 10, 0, 0, 0, tzinfo=UTC))
    assert mean_sidereal_time(jd) == pytest.approx(197.693195, abs=1e-6)


def test_mean_sidereal_time_advances_about_361_degrees_per_day() -> None:
    # ~360.98565°/día: un poco más que una vuelta completa por día solar,
    # por el movimiento orbital de la Tierra (Meeus cap. 12).
    jd = J2000
    delta = mean_sidereal_time(jd + 1) - mean_sidereal_time(jd)
    assert delta == pytest.approx(0.98564736629, abs=1e-9)


def test_mean_sidereal_time_normalized_to_0_360() -> None:
    for jd in [J2000, J2000 + 12_345.6, J2000 - 98_765.4]:
        assert 0 <= mean_sidereal_time(jd) < 360
