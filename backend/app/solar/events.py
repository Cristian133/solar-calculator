"""Orto, tránsito y ocaso del Sol (Meeus cap. 15).

Simplificación respecto al algoritmo del libro: Meeus interpola α/δ a
partir de tres muestras diarias (día anterior/actual/siguiente) porque
parte de tablas de efemérides discretas. Acá `app.solar.coordinates` es
continuo en T, así que en cada iteración evaluamos directamente la
posición solar en el instante exacto — la interpolación de 3 puntos del
libro queda innecesaria.

Como en `coordinates.py`, se ignora ΔT (diferencia TD-UT) y la ecuación de
los equinoccios (ver `app.solar.time.mean_sidereal_time`): ambas son del
orden de segundos, muy por debajo de la precisión que necesita esta app.

Convención de longitud: positiva al este (a diferencia del propio libro de
Meeus, que la toma positiva al oeste), por ser la convención moderna más
intuitiva (coincide, por ejemplo, con la de coordenadas GPS).
"""

import math
from dataclasses import dataclass
from datetime import UTC, date, datetime

from app.solar.coordinates import declination, right_ascension
from app.solar.horizontal import altitude, hour_angle, local_sidereal_time
from app.solar.time import datetime_from_julian_day, julian_century, julian_day, mean_sidereal_time

STANDARD_ALTITUDE_SUN = -0.8333
"""h0: altitud aparente estándar de orto/ocaso del Sol, en grados (Meeus
cap. 15) — incluye la refracción atmosférica típica en el horizonte (~34')
y el semidiámetro solar (~16'), no la posición geométrica exacta."""

_MAX_ITERATIONS = 3


@dataclass(frozen=True)
class SunDay:
    """Eventos solares de un día para un observador dado, en UT.

    `sunrise`/`sunset` son `None` cuando el Sol no cruza `altitude_deg` ese
    día; en ese caso `always_above` indica si quedó todo el día por encima
    (sol de medianoche) o por debajo (noche polar) de esa altitud.
    """

    transit: datetime
    sunrise: datetime | None
    sunset: datetime | None
    always_above: bool | None


def _sun_hour_angle(jd: float, longitude_deg: float) -> float:
    """Ángulo horario (H) del Sol en `jd`, en grados, normalizado a
    (-180, 180]. Positivo del mediodía solar hacia adelante (tarde)."""
    t = julian_century(jd)
    alpha = right_ascension(t)
    lst = local_sidereal_time(mean_sidereal_time(jd), longitude_deg)
    return hour_angle(lst, alpha)


def _hour_angle_at_altitude(
    latitude_deg: float, declination_deg: float, altitude_deg: float
) -> float | None:
    """H0 (grados, en [0, 180]): semiarco diurno al que el Sol cruza
    `altitude_deg` para la latitud y declinación dadas.

    `None` si el Sol no cruza esa altitud ese día — circumpolar (siempre
    por encima) o nunca visible (siempre por debajo); distinguir cuál es
    responsabilidad de quien llama, comparando con la altitud a mediodía.
    """
    phi = math.radians(latitude_deg)
    delta = math.radians(declination_deg)
    cos_h0 = (math.sin(math.radians(altitude_deg)) - math.sin(phi) * math.sin(delta)) / (
        math.cos(phi) * math.cos(delta)
    )
    if cos_h0 < -1 or cos_h0 > 1:
        return None
    return math.degrees(math.acos(cos_h0))


def solar_transit(day: date, longitude_deg: float) -> datetime:
    """Instante (UT) del tránsito solar (mediodía solar aparente) para la
    fecha y longitud (positiva al este) dadas."""
    jd0 = julian_day(datetime(day.year, day.month, day.day, tzinfo=UTC))
    m = (0.5 - longitude_deg / 360) % 1

    for _ in range(_MAX_ITERATIONS):
        m -= _sun_hour_angle(jd0 + m, longitude_deg) / 360

    return datetime_from_julian_day(jd0 + m)


def sunrise_sunset(
    day: date,
    latitude_deg: float,
    longitude_deg: float,
    altitude_deg: float = STANDARD_ALTITUDE_SUN,
) -> SunDay:
    """Orto y ocaso (UT) del Sol para la fecha, latitud y longitud (positiva
    al este) dadas, a la altitud aparente `altitude_deg` (por defecto,
    `STANDARD_ALTITUDE_SUN`)."""
    jd0 = julian_day(datetime(day.year, day.month, day.day, tzinfo=UTC))
    transit = solar_transit(day, longitude_deg)
    m_transit = julian_day(transit) - jd0

    delta_at_transit = declination(julian_century(jd0 + m_transit))
    h0 = _hour_angle_at_altitude(latitude_deg, delta_at_transit, altitude_deg)

    if h0 is None:
        altitude_at_transit = altitude(latitude_deg, delta_at_transit, 0.0)
        return SunDay(
            transit=transit,
            sunrise=None,
            sunset=None,
            always_above=altitude_at_transit > altitude_deg,
        )

    sunrise = _refine_horizon_crossing(
        jd0, m_transit - h0 / 360, latitude_deg, longitude_deg, altitude_deg
    )
    sunset = _refine_horizon_crossing(
        jd0, m_transit + h0 / 360, latitude_deg, longitude_deg, altitude_deg
    )
    return SunDay(transit=transit, sunrise=sunrise, sunset=sunset, always_above=None)


def _refine_horizon_crossing(
    jd0: float,
    m_initial: float,
    latitude_deg: float,
    longitude_deg: float,
    altitude_deg: float,
) -> datetime:
    """Refina por iteración el instante (fracción de día `m` desde `jd0`) en
    que el Sol cruza `altitude_deg`, y lo devuelve como `datetime` UT."""
    m = m_initial

    for _ in range(_MAX_ITERATIONS):
        jd = jd0 + m
        t = julian_century(jd)
        delta_deg = declination(t)
        h_deg = _sun_hour_angle(jd, longitude_deg)
        current_altitude = altitude(latitude_deg, delta_deg, h_deg)

        sin_h = math.sin(math.radians(h_deg))
        if sin_h == 0:
            break
        cos_delta = math.cos(math.radians(delta_deg))
        cos_phi = math.cos(math.radians(latitude_deg))
        m += (current_altitude - altitude_deg) / (360 * cos_delta * cos_phi * sin_h)

    return datetime_from_julian_day(jd0 + m)
