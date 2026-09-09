import numpy as np
import pytest

from app.solar.irradiance import (
    SOLAR_CONSTANT,
    air_mass,
    clear_sky_irradiance,
    direct_beam_irradiance,
    extraterrestrial_irradiance,
)


def test_extraterrestrial_irradiance_at_one_au_equals_solar_constant() -> None:
    assert extraterrestrial_irradiance(1.0) == pytest.approx(SOLAR_CONSTANT)


def test_extraterrestrial_irradiance_scales_as_inverse_square() -> None:
    assert extraterrestrial_irradiance(2.0) == pytest.approx(SOLAR_CONSTANT / 4)


def test_air_mass_is_approximately_1_at_zenith() -> None:
    # AM=1 exacto en el cenit es la definición idealizada (trayecto vertical
    # mínimo); Kasten-Young da un valor levemente distinto por su término de
    # corrección empírico.
    assert air_mass(90.0) == pytest.approx(1.0, abs=0.001)


def test_air_mass_is_approximately_1_5_at_standard_test_condition_angle() -> None:
    # AM1.5 (48.19° de ángulo cenital) es la condición estándar de la
    # industria fotovoltaica (STC) para especificar paneles solares — un
    # hecho de conocimiento general, no un valor de tabla de este proyecto.
    zenith_deg = 48.19
    assert air_mass(90.0 - zenith_deg) == pytest.approx(1.5, abs=0.01)


def test_air_mass_increases_as_sun_approaches_horizon() -> None:
    assert air_mass(80.0) < air_mass(45.0) < air_mass(20.0) < air_mass(5.0)


def test_direct_beam_irradiance_is_zero_at_and_below_horizon() -> None:
    assert direct_beam_irradiance(0.0, 1.0) == 0.0
    assert direct_beam_irradiance(-10.0, 1.0) == 0.0
    assert direct_beam_irradiance(-70.0, 1.0) == 0.0  # no debe dar NaN


def test_direct_beam_irradiance_at_zenith_is_plausible_clear_sky_value() -> None:
    # ~950 W/m² en el cenit con cielo despejado es el orden de magnitud
    # bien conocido (la irradiancia extraterrestre es 1361 W/m², atenuada
    # por la atmósfera incluso en el mejor de los casos).
    value = direct_beam_irradiance(90.0, 1.0)
    assert 900 < value < 1000


def test_direct_beam_irradiance_increases_with_altitude() -> None:
    assert (
        direct_beam_irradiance(10.0, 1.0)
        < direct_beam_irradiance(45.0, 1.0)
        < direct_beam_irradiance(90.0, 1.0)
    )


def test_clear_sky_irradiance_is_zero_at_and_below_horizon() -> None:
    assert clear_sky_irradiance(0.0, 1.0) == 0.0
    assert clear_sky_irradiance(-10.0, 1.0) == 0.0


def test_clear_sky_irradiance_equals_direct_beam_projected_by_sine_of_altitude() -> None:
    for altitude_deg in [10.0, 30.0, 60.0, 89.0]:
        expected = direct_beam_irradiance(altitude_deg, 1.0) * np.sin(np.radians(altitude_deg))
        assert clear_sky_irradiance(altitude_deg, 1.0) == pytest.approx(expected)


def test_clear_sky_irradiance_less_than_direct_beam_away_from_zenith() -> None:
    # La proyección horizontal siempre reduce la potencia recibida salvo
    # exactamente en el cenit (sin(90°)=1).
    for altitude_deg in [10.0, 30.0, 60.0]:
        assert clear_sky_irradiance(altitude_deg, 1.0) < direct_beam_irradiance(altitude_deg, 1.0)
    assert clear_sky_irradiance(90.0, 1.0) == pytest.approx(direct_beam_irradiance(90.0, 1.0))


def test_functions_vectorize_over_numpy_arrays() -> None:
    altitudes = np.array([-10.0, 0.0, 30.0, 90.0])
    radii = np.full_like(altitudes, 1.0)
    result = clear_sky_irradiance(altitudes, radii)
    assert list(result[:2]) == [0.0, 0.0]
    assert result[2] > 0
    assert result[3] == pytest.approx(direct_beam_irradiance(90.0, 1.0))
