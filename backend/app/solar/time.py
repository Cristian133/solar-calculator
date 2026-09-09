"""Tiempo: Día Juliano (JD) y siglos julianos desde J2000.0.

Toda la app calcula internamente en Tiempo Universal (UT); la conversión a
hora local del observador se hace en la capa de presentación (ver
docs/plan_tecnico.md, sección 4.1). Este módulo asume calendario gregoriano
(válido para fechas posteriores a 1582-10-15); no maneja calendario juliano.
"""

import math
from datetime import UTC, datetime, timedelta

J2000 = 2451545.0
"""JD de la época estándar J2000.0 (2000-01-01 12:00 UT)."""

_DAYS_PER_JULIAN_CENTURY = 36525.0


def julian_day(moment: datetime) -> float:
    """Convierte un instante a Día Juliano (JD).

    `moment` puede ser naive (se asume ya en UT) o timezone-aware (se
    convierte a UT antes de calcular).
    """
    if moment.tzinfo is not None:
        moment = moment.astimezone(UTC).replace(tzinfo=None)

    year, month = moment.year, moment.month
    day = (
        moment.day
        + moment.hour / 24
        + moment.minute / 1_440
        + (moment.second + moment.microsecond / 1e6) / 86_400
    )

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + a // 4

    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5


def julian_century(jd: float) -> float:
    """Siglos julianos transcurridos desde J2000.0 (T)."""
    return (jd - J2000) / _DAYS_PER_JULIAN_CENTURY


def datetime_from_julian_day(jd: float) -> datetime:
    """Convierte un Día Juliano (JD) a un instante UTC.

    Inversa de `julian_day` (Meeus cap. 7): como esa función, asume
    calendario gregoriano proléptico en todo el rango de fechas (sin la
    rama juliana previa a 1582 del algoritmo original del libro), para que
    el redondeo de ambas funciones sea consistente entre sí.
    """
    jd_shifted = jd + 0.5
    z = math.floor(jd_shifted)
    f = jd_shifted - z

    # INT() en Meeus es floor (mayor entero <= x), no truncamiento — importa
    # para fechas donde estos cocientes dan negativo.
    alpha = math.floor((z - 1867216.25) / 36524.25)
    a = z + 1 + alpha - alpha // 4

    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)

    day = b - d - math.floor(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    day_int = int(day)
    seconds_into_day = round((day - day_int) * 86_400)
    return datetime(year, month, day_int, tzinfo=UTC) + timedelta(seconds=seconds_into_day)


def mean_sidereal_time(jd: float) -> float:
    """Tiempo sidéreo medio en Greenwich (θ0), en grados, normalizado a
    [0, 360) (Meeus cap. 12, ecuación 12.4).

    Válido para cualquier instante `jd`, no solo 0h UT. No incluye la
    ecuación de los equinoccios (corrección por nutación): la diferencia
    con el tiempo sidéreo *aparente* es del orden de 1 segundo de tiempo,
    despreciable frente a otras aproximaciones de baja precisión ya
    asumidas en esta app (ver nota de ΔT en `app.solar.coordinates`).
    """
    t = julian_century(jd)
    theta0 = 280.46061837 + 360.98564736629 * (jd - J2000) + 0.000387933 * t**2 - t**3 / 38_710_000
    return theta0 % 360
