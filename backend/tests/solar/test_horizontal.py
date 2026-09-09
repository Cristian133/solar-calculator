import pytest

from app.solar.horizontal import altitude, azimuth, hour_angle, local_sidereal_time

# Todas las identidades de este archivo son exactas (geometría esférica
# básica o hechos astronómicos de conocimiento general), no valores de
# tabla transcriptos a mano.


def test_local_sidereal_time_adds_longitude() -> None:
    assert local_sidereal_time(100.0, 30.0) == pytest.approx(130.0)


def test_local_sidereal_time_normalized_to_0_360() -> None:
    assert local_sidereal_time(350.0, 30.0) == pytest.approx(20.0)
    assert local_sidereal_time(10.0, -30.0) == pytest.approx(340.0)


def test_hour_angle_is_local_sidereal_time_minus_right_ascension() -> None:
    assert hour_angle(100.0, 40.0) == pytest.approx(60.0)


def test_hour_angle_normalized_to_pm_180() -> None:
    assert hour_angle(10.0, 200.0) == pytest.approx(170.0)
    assert hour_angle(350.0, 10.0) == pytest.approx(-20.0)


@pytest.mark.parametrize("latitude_deg", [-60.0, 0.0, 60.0])
def test_altitude_at_transit_equals_90_minus_zenith_distance(latitude_deg: float) -> None:
    # H=0 (tránsito) con el Sol exactamente en el cenit del observador.
    assert altitude(latitude_deg, latitude_deg, 0.0) == pytest.approx(90.0)


@pytest.mark.parametrize("latitude_deg", [-60.0, 0.0, 60.0])
def test_altitude_is_zero_six_hours_from_transit_when_declination_is_zero(
    latitude_deg: float,
) -> None:
    # H=±90° con declinación 0: el Sol está justo en el horizonte,
    # independientemente de la latitud (equinoccio, cualquier lugar).
    assert altitude(latitude_deg, 0.0, 90.0) == pytest.approx(0.0, abs=1e-9)
    assert altitude(latitude_deg, 0.0, -90.0) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("latitude_deg", [-80.0, -10.0, 10.0, 80.0])
def test_azimuth_is_east_at_sunrise_and_west_at_sunset_on_equinox(latitude_deg: float) -> None:
    # Hecho de conocimiento general: en el equinoccio, el Sol sale
    # exactamente por el Este y se pone exactamente por el Oeste en
    # cualquier lugar de la Tierra (declinación 0, H=∓90°).
    assert azimuth(latitude_deg, 0.0, -90.0) == pytest.approx(90.0)  # orto: Este
    assert azimuth(latitude_deg, 0.0, 90.0) == pytest.approx(270.0)  # ocaso: Oeste


def test_azimuth_at_transit_is_north_when_latitude_less_than_declination() -> None:
    # A mediodía solar, si la latitud del observador es menor que la
    # declinación del Sol, el Sol queda al Norte (ej. Buenos Aires en
    # diciembre: lat -34.6° < dec +23.4°, el sol de mediodía está al norte
    # y las sombras apuntan al sur, como se ve a simple vista en el
    # hemisferio sur).
    assert azimuth(latitude_deg=-34.6, declination_deg=23.4, hour_angle_deg=0.0) == pytest.approx(
        0.0
    )


def test_azimuth_at_transit_is_south_when_latitude_greater_than_declination() -> None:
    # Caso simétrico: latitud > declinación -> el Sol de mediodía queda al
    # Sur (ej. la mayor parte del hemisferio norte templado).
    assert azimuth(latitude_deg=10.0, declination_deg=-23.4, hour_angle_deg=0.0) == pytest.approx(
        180.0
    )
