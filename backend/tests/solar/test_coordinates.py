import pytest

from app.solar.coordinates import (
    _equatorial_from_ecliptic,
    apparent_longitude,
    apparent_obliquity,
    declination,
    eccentricity,
    mean_anomaly,
    mean_longitude,
    radius_vector,
    right_ascension,
)

# Meeus, Astronomical Algorithms cap. 25, ejemplo 25.a: 1992-10-13.0 TD.
EXAMPLE_25A_T = -0.072183436

# Valores de referencia independientes para esa misma fecha, calculados con
# la teoría VSOP87 de alta precisión (no el método de baja precisión que
# implementa este módulo) — longitud/radio vector aparentes citados en la
# documentación de PyMeeus (`Sun.apparent_geocentric_position`, basada en el
# mismo ejemplo del libro). Sirven para verificar que el método de baja
# precisión cae dentro de su propio margen de error anunciado (< 0.01°,
# Meeus cap. 25) respecto a un resultado de referencia independiente, sin
# depender de transcribir a mano las cifras intermedias del libro.
_VSOP87_APPARENT_LONGITUDE = 199 + 54 / 60 + 21.548 / 3600  # 199°54'21.548"
_VSOP87_RADIUS_VECTOR = 0.99760852


def test_mean_longitude_at_j2000() -> None:
    assert mean_longitude(0.0) == pytest.approx(280.46646)


def test_mean_anomaly_at_j2000() -> None:
    assert mean_anomaly(0.0) == pytest.approx(357.52911)


def test_eccentricity_at_j2000() -> None:
    assert eccentricity(0.0) == pytest.approx(0.016708634)


def test_apparent_longitude_within_low_precision_error_bound() -> None:
    diff = abs(apparent_longitude(EXAMPLE_25A_T) - _VSOP87_APPARENT_LONGITUDE)
    assert diff < 0.01


def test_radius_vector_within_low_precision_error_bound() -> None:
    diff = abs(radius_vector(EXAMPLE_25A_T) - _VSOP87_RADIUS_VECTOR)
    assert diff < 1e-4


@pytest.mark.parametrize("obliquity", [21.0, 23.43999, 26.0])
def test_equatorial_from_ecliptic_at_march_equinox(obliquity: float) -> None:
    # λ = 0°: el Sol cruza el ecuador celeste, sea cual sea la oblicuidad.
    alpha, delta = _equatorial_from_ecliptic(0.0, obliquity)
    assert alpha == pytest.approx(0.0, abs=1e-9)
    assert delta == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("obliquity", [21.0, 23.43999, 26.0])
def test_equatorial_from_ecliptic_at_june_solstice(obliquity: float) -> None:
    # λ = 90°: declinación máxima, igual a la oblicuidad de la eclíptica.
    alpha, delta = _equatorial_from_ecliptic(90.0, obliquity)
    assert alpha == pytest.approx(90.0)
    assert delta == pytest.approx(obliquity)


@pytest.mark.parametrize("obliquity", [21.0, 23.43999, 26.0])
def test_equatorial_from_ecliptic_at_september_equinox(obliquity: float) -> None:
    alpha, delta = _equatorial_from_ecliptic(180.0, obliquity)
    assert alpha == pytest.approx(180.0)
    assert delta == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("obliquity", [21.0, 23.43999, 26.0])
def test_equatorial_from_ecliptic_at_december_solstice(obliquity: float) -> None:
    # λ = 270°: declinación mínima (negativa), simétrica al solsticio de junio.
    alpha, delta = _equatorial_from_ecliptic(270.0, obliquity)
    assert alpha == pytest.approx(270.0)
    assert delta == pytest.approx(-obliquity)


def test_right_ascension_and_declination_consistent_with_helper() -> None:
    """`right_ascension`/`declination` deben coincidir con aplicar
    `_equatorial_from_ecliptic` a la longitud y oblicuidad aparentes del
    mismo instante (evita que las dos funciones públicas se desincronicen
    entre sí con el paso del tiempo)."""
    expected_alpha, expected_delta = _equatorial_from_ecliptic(
        apparent_longitude(EXAMPLE_25A_T), apparent_obliquity(EXAMPLE_25A_T)
    )
    assert right_ascension(EXAMPLE_25A_T) == pytest.approx(expected_alpha)
    assert declination(EXAMPLE_25A_T) == pytest.approx(expected_delta)
