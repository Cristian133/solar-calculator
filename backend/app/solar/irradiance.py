"""Irradiancia solar en cielo despejado (fuente de respaldo: Meeus no
cubre radiometría; ver docs/plan_tecnico.md, secciones 4.6 y 10).

Modelo elegido (resuelve el pendiente abierto de la sección 10): masa de
aire relativa según Kasten y Young (1989), y atenuación atmosférica según
el modelo simplificado de cielo despejado de Meinel & Meinel (1976),
I = I0 · 0.7^(AM^0.678) — ambos de uso extendido en ingeniería solar (ej.
Duffie & Beckman, *Solar Engineering of Thermal Processes*; PVEducation.org)
y no específicos de una única fuente con derechos reservados.

Es un modelo teórico simplificado: cielo despejado (sin nubes), sin
componente difusa por dispersión atmosférica ni reflejada por el entorno
— solo irradiancia directa proyectada sobre una superficie horizontal.
Sirve para una estimación de orden de magnitud (punto 5), no para diseño
de sistemas fotovoltaicos de precisión.

Como en `coordinates.py`/`horizontal.py`, se usa `numpy` para que estas
funciones vectoricen automáticamente sobre arrays."""

import numpy as np
from numpy.typing import ArrayLike

from app.solar.coordinates import FloatOrArray

SOLAR_CONSTANT = 1361.0
"""Constante solar (W/m²): irradiancia extraterrestre media a 1 UA del Sol
(TSI promedio de la era de medición satelital)."""


def extraterrestrial_irradiance(radius_vector_au: ArrayLike) -> FloatOrArray:
    """Irradiancia extraterrestre (W/m²) a la distancia Tierra-Sol dada
    (`radius_vector_au`, en UA — ver `coordinates.radius_vector`)."""
    return SOLAR_CONSTANT / radius_vector_au**2


def air_mass(altitude_deg: ArrayLike) -> FloatOrArray:
    """Masa de aire relativa (adimensional, 1 en el cenit) para la altitud
    solar dada, según el modelo de Kasten y Young (1989).

    Válida para altitud en [0°, 90°]; para altitud negativa (sol bajo el
    horizonte) el término `(96.07995 - zenith_deg)` puede volverse
    negativo y la potencia fraccionaria da `nan` — quien llama debe
    filtrar esos casos (`direct_beam_irradiance` ya lo hace)."""
    zenith_deg = 90.0 - altitude_deg
    return 1.0 / (np.cos(np.radians(zenith_deg)) + 0.50572 * (96.07995 - zenith_deg) ** (-1.6364))


def direct_beam_irradiance(altitude_deg: ArrayLike, radius_vector_au: ArrayLike) -> FloatOrArray:
    """Irradiancia solar directa (normal al haz), en W/m², en cielo
    despejado, para la altitud solar y el radio vector Tierra-Sol dados:
    irradiancia extraterrestre atenuada por masa de aire (Meinel & Meinel,
    1976): I = I0 · 0.7^(AM^0.678).

    Cero cuando el Sol está en o bajo el horizonte (`altitude_deg <= 0`).
    """
    altitude_deg = np.asarray(altitude_deg, dtype=float)
    clipped_altitude = np.clip(altitude_deg, 0.0, None)  # evita AM indefinida bajo el horizonte
    am = air_mass(clipped_altitude)
    i0 = extraterrestrial_irradiance(radius_vector_au)
    direct = i0 * 0.7 ** (am**0.678)
    return np.where(altitude_deg > 0, direct, 0.0)


def clear_sky_irradiance(altitude_deg: ArrayLike, radius_vector_au: ArrayLike) -> FloatOrArray:
    """Irradiancia solar (W/m²) sobre una superficie horizontal, en cielo
    despejado: `direct_beam_irradiance` proyectada según el ángulo de
    incidencia respecto al plano horizontal (factor sin(altitud), el
    "efecto coseno" respecto al cenit).

    Cero (no `-0.0`: se fuerza explícitamente) cuando el Sol está en o
    bajo el horizonte."""
    altitude_deg = np.asarray(altitude_deg, dtype=float)
    direct = direct_beam_irradiance(altitude_deg, radius_vector_au)
    horizontal = direct * np.sin(np.radians(altitude_deg))
    return np.where(altitude_deg > 0, horizontal, 0.0)
