import numpy as np
import pytest

from app.solar.refraction import apparent_altitude, true_altitude


def test_true_altitude_at_apparent_horizon_is_about_34_arcminutes_below() -> None:
    # Hecho de conocimiento general en astronomía: en el horizonte, la
    # refracción atmosférica estándar es de ~34' — el valor detrás del
    # h0 = -0.5667° usado para estrellas en Meeus cap. 15 (y, sumado al
    # semidiámetro solar, de STANDARD_ALTITUDE_SUN en events.py).
    assert true_altitude(0.0) == pytest.approx(-34.0 / 60, abs=0.02)


def test_apparent_altitude_negligible_correction_at_zenith() -> None:
    assert apparent_altitude(90.0) == pytest.approx(90.0, abs=0.01)


def test_true_altitude_negligible_correction_at_zenith() -> None:
    assert true_altitude(90.0) == pytest.approx(90.0, abs=0.01)


def test_apparent_altitude_is_above_true_altitude_near_horizon() -> None:
    # La refracción siempre "levanta" los objetos cerca del horizonte.
    for true_alt in [-1.0, 0.0, 5.0, 20.0]:
        assert apparent_altitude(true_alt) > true_alt


def test_refraction_correction_decreases_with_altitude() -> None:
    def correction_at(h: float) -> float:
        return apparent_altitude(h) - h

    assert correction_at(0.0) > correction_at(20.0) > correction_at(45.0) > correction_at(80.0)


def test_apparent_and_true_altitude_are_approximately_inverse() -> None:
    # Sæmundsson y Bennett son ajustes empíricos independientes, no
    # inversas algebraicas exactas una de la otra -- pero deben acercarse
    # mucho al aplicarlas en cadena.
    for h in [0.0, 10.0, 45.0, 89.0]:
        assert true_altitude(apparent_altitude(h)) == pytest.approx(h, abs=0.01)


def test_pressure_and_temperature_reduce_correction_in_thinner_air() -> None:
    # Menos presión / más temperatura -> aire menos denso -> menos
    # refracción (la corrección estándar es para 1010mb/10°C).
    standard = true_altitude(0.0)
    thinner_air = true_altitude(0.0, pressure_mbar=900.0, temperature_c=25.0)
    assert abs(thinner_air) < abs(standard)


def test_functions_vectorize_over_numpy_arrays() -> None:
    true_alts = np.array([-1.0, 0.0, 45.0, 90.0])
    result = apparent_altitude(true_alts)
    assert len(result) == 4
    assert all(result[i] > true_alts[i] for i in range(3))  # cerca de horizonte/cielo medio
    assert result[3] == pytest.approx(90.0, abs=0.01)  # cenit
