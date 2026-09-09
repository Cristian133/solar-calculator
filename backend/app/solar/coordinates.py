"""Posición solar geocéntrica (Meeus cap. 25, método de baja precisión,
error < 0.01°).

Todas las funciones reciben `t`: siglos julianos desde J2000.0 (ver
`app.solar.time.julian_century`). Los ángulos se expresan en grados en las
fronteras públicas del módulo; la conversión a radianes es un detalle
interno de cada función.

Nota: el `t` de estas fórmulas corresponde a Tiempo Dinámico (TD/TT), no a
UT — la diferencia (ΔT) es del orden de segundos y no afecta la precisión
que necesita esta app (ver docs/plan_tecnico.md, sección 10, pendiente
abierto de zona horaria; ΔT es un refinamiento futuro, no bloqueante aquí).
"""

import math


def mean_longitude(t: float) -> float:
    """Longitud media del Sol (L0), en grados, normalizada a [0, 360)."""
    l0 = 280.46646 + t * (36000.76983 + t * 0.0003032)
    return l0 % 360


def mean_anomaly(t: float) -> float:
    """Anomalía media del Sol (M), en grados, normalizada a [0, 360)."""
    m = 357.52911 + t * (35999.05029 - t * 0.0001537)
    return m % 360


def eccentricity(t: float) -> float:
    """Excentricidad de la órbita terrestre (e), adimensional."""
    return 0.016708634 - t * (0.000042037 + t * 0.0000001267)


def equation_of_center(t: float) -> float:
    """Ecuación del centro del Sol (C), en grados."""
    m = math.radians(mean_anomaly(t))
    return (
        (1.914602 - t * (0.004817 + t * 0.000014)) * math.sin(m)
        + (0.019993 - t * 0.000101) * math.sin(2 * m)
        + 0.000289 * math.sin(3 * m)
    )


def true_longitude(t: float) -> float:
    """Longitud verdadera del Sol (☉ = L0 + C), en grados, normalizada."""
    return (mean_longitude(t) + equation_of_center(t)) % 360


def true_anomaly(t: float) -> float:
    """Anomalía verdadera del Sol (v = M + C), en grados, normalizada."""
    return (mean_anomaly(t) + equation_of_center(t)) % 360


def radius_vector(t: float) -> float:
    """Radio vector Tierra-Sol (R), en unidades astronómicas (UA)."""
    e = eccentricity(t)
    v = math.radians(true_anomaly(t))
    return (1.000001018 * (1 - e**2)) / (1 + e * math.cos(v))


def _ascending_node_longitude(t: float) -> float:
    """Longitud del nodo ascendente de la Luna (Ω), en grados.

    Término auxiliar de baja precisión usado solo para corregir la longitud
    aparente y la oblicuidad por nutación (no es un resultado público del
    módulo).
    """
    return 125.04 - 1934.136 * t


def apparent_longitude(t: float) -> float:
    """Longitud aparente del Sol (λ), en grados, normalizada a [0, 360).

    Longitud verdadera corregida por nutación en longitud y aberración
    (término aproximado de baja precisión, suficiente para el error
    objetivo de 0.01°).
    """
    omega = math.radians(_ascending_node_longitude(t))
    return (true_longitude(t) - 0.00569 - 0.00478 * math.sin(omega)) % 360


def mean_obliquity(t: float) -> float:
    """Oblicuidad media de la eclíptica (ε0), en grados."""
    seconds = 21.448 - t * (46.8150 + t * (0.00059 - t * 0.001813))
    return 23 + 26 / 60 + seconds / 3600


def apparent_obliquity(t: float) -> float:
    """Oblicuidad de la eclíptica corregida por nutación (ε), en grados."""
    omega = math.radians(_ascending_node_longitude(t))
    return mean_obliquity(t) + 0.00256 * math.cos(omega)


def _equatorial_from_ecliptic(longitude_deg: float, obliquity_deg: float) -> tuple[float, float]:
    """Transforma longitud eclíptica (β = 0, caso del Sol) a coordenadas
    ecuatoriales (α, δ), ambas en grados y α normalizada a [0, 360).

    Aislada del resto del módulo para poder verificarla con identidades
    exactas (equinoccios/solsticios) sin depender de las fórmulas de
    posición solar.
    """
    lam = math.radians(longitude_deg)
    epsilon = math.radians(obliquity_deg)
    alpha = math.atan2(math.cos(epsilon) * math.sin(lam), math.cos(lam))
    delta = math.asin(math.sin(epsilon) * math.sin(lam))
    return math.degrees(alpha) % 360, math.degrees(delta)


def right_ascension(t: float) -> float:
    """Ascensión recta aparente del Sol (α), en grados, normalizada a
    [0, 360)."""
    alpha, _ = _equatorial_from_ecliptic(apparent_longitude(t), apparent_obliquity(t))
    return alpha


def declination(t: float) -> float:
    """Declinación aparente del Sol (δ), en grados."""
    _, delta = _equatorial_from_ecliptic(apparent_longitude(t), apparent_obliquity(t))
    return delta
