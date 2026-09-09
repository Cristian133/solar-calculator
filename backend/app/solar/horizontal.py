"""Transformación de coordenadas ecuatoriales a horizontales: ángulo
horario, altitud y azimut (Meeus cap. 13).

Base directa de la trayectoria solar y la altitud a mediodía (puntos 3 y 4
del plan técnico, sección 5).

Convenciones:
- Longitud positiva al este (a diferencia del propio Meeus, que la toma
  positiva al oeste) — es la convención moderna más intuitiva, coincide
  con la de coordenadas GPS.
- Azimut medido desde el Norte en sentido horario (0°=N, 90°=E, 180°=S,
  270°=O) — convención de rumbo/compass moderna; Meeus lo mide desde el
  Sur.
"""

import math


def _wrap180(angle_deg: float) -> float:
    """Normaliza un ángulo a (-180, 180]."""
    return (angle_deg + 180) % 360 - 180


def local_sidereal_time(greenwich_sidereal_time_deg: float, longitude_deg: float) -> float:
    """Tiempo sidéreo local, en grados, normalizado a [0, 360)."""
    return (greenwich_sidereal_time_deg + longitude_deg) % 360


def hour_angle(local_sidereal_time_deg: float, right_ascension_deg: float) -> float:
    """Ángulo horario (H), en grados, normalizado a (-180, 180].

    H = tiempo sidéreo local - ascensión recta: negativo antes del tránsito
    (mañana), positivo después (tarde)."""
    return _wrap180(local_sidereal_time_deg - right_ascension_deg)


def altitude(latitude_deg: float, declination_deg: float, hour_angle_deg: float) -> float:
    """Altitud (h) del Sol sobre el horizonte, en grados."""
    phi = math.radians(latitude_deg)
    delta = math.radians(declination_deg)
    h = math.radians(hour_angle_deg)
    sin_altitude = math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.cos(h)
    return math.degrees(math.asin(sin_altitude))


def azimuth(latitude_deg: float, declination_deg: float, hour_angle_deg: float) -> float:
    """Azimut (A) del Sol, en grados [0, 360), medido desde el Norte en
    sentido horario.

    Matemáticamente indeterminado cuando el Sol está exactamente en el
    cenit del observador (altitud 90°, latitud = declinación y H=0); en ese
    punto límite esta función devuelve 180° por convención de `atan2`, sin
    significado físico especial.
    """
    phi = math.radians(latitude_deg)
    delta = math.radians(declination_deg)
    h = math.radians(hour_angle_deg)
    y = math.sin(h)
    x = math.cos(h) * math.sin(phi) - math.tan(delta) * math.cos(phi)
    return (math.degrees(math.atan2(y, x)) + 180) % 360
