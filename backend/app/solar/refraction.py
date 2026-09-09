"""Refracción atmosférica (Meeus cap. 16).

Corrige la diferencia entre altitud verdadera (geométrica, la que
devuelve `app.solar.horizontal.altitude`) y altitud aparente (la que
realmente se observa: la atmósfera desvía la luz y "levanta" los objetos
cerca del horizonte). El efecto es máximo en el horizonte (~34', el valor
detrás de `STANDARD_ALTITUDE_SUN` en `events.py`) y despreciable cerca
del cenit.

Fórmulas de Sæmundsson (verdadera → aparente, ec. 16.4) y Bennett
(aparente → verdadera, ec. 16.3), para condiciones atmosféricas estándar
(1010 mb, 10°C) con corrección opcional de presión/temperatura — ambas
de uso extendido en almanaques y software astronómico, no exclusivas de
un único libro con derechos reservados.

Válidas cerca y por encima del horizonte; por debajo de eso el objeto ya
no es visible y la refracción deja de tener sentido físico. Se acota
internamente la altitud usada en la fórmula (no el resultado) para evitar
inestabilidad numérica cerca de esa cota, no para representar el efecto
con precisión ahí — igual que el recorte de masa de aire en
`app.solar.irradiance`.

Como en el resto de `app.solar`, se usa `numpy` para vectorizar
automáticamente sobre arrays."""

import numpy as np
from numpy.typing import ArrayLike

from app.solar.coordinates import FloatOrArray

_MIN_ALTITUDE_FOR_FORMULA = -1.9
"""Cota inferior de altitud (grados) para evaluar las fórmulas."""


def _pressure_temperature_factor(
    pressure_mbar: ArrayLike, temperature_c: ArrayLike
) -> FloatOrArray:
    """Factor de corrección por presión/temperatura respecto a las
    condiciones estándar (1010 mb, 10°C) que asumen las fórmulas base."""
    return (pressure_mbar / 1010.0) * (283.0 / (273.0 + temperature_c))


def apparent_altitude(
    true_altitude_deg: ArrayLike,
    pressure_mbar: ArrayLike = 1010.0,
    temperature_c: ArrayLike = 10.0,
) -> FloatOrArray:
    """Altitud aparente (la que se observa), en grados, a partir de la
    altitud verdadera (geométrica) — fórmula de Sæmundsson (1986)."""
    h = np.clip(np.asarray(true_altitude_deg, dtype=float), _MIN_ALTITUDE_FOR_FORMULA, None)
    r_arcmin = 1.02 / np.tan(np.radians(h + 10.3 / (h + 5.11)))
    r_arcmin = r_arcmin * _pressure_temperature_factor(pressure_mbar, temperature_c)
    return true_altitude_deg + r_arcmin / 60


def true_altitude(
    apparent_altitude_deg: ArrayLike,
    pressure_mbar: ArrayLike = 1010.0,
    temperature_c: ArrayLike = 10.0,
) -> FloatOrArray:
    """Altitud verdadera (geométrica), en grados, a partir de la altitud
    aparente (la observada) — fórmula de Bennett (1982)."""
    h = np.clip(np.asarray(apparent_altitude_deg, dtype=float), _MIN_ALTITUDE_FOR_FORMULA, None)
    r_arcmin = 1.0 / np.tan(np.radians(h + 7.31 / (h + 4.4)))
    r_arcmin = r_arcmin * _pressure_temperature_factor(pressure_mbar, temperature_c)
    return apparent_altitude_deg - r_arcmin / 60
