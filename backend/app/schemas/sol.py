"""Modelos Pydantic de request/response del endpoint `/sol` (ver
docs/plan_tecnico.md, sección 5)."""

from datetime import date, datetime

from pydantic import BaseModel


class DailySun(BaseModel):
    """Eventos solares de un día dentro de la evolución anual.

    `transit` siempre está presente. `sunrise`/`sunset` son `None` en un
    día polar (sol de medianoche o noche polar) — `always_above` distingue
    cuál de los dos es, y en ese caso `day_length_hours` también es `None`.
    """

    date: date
    transit: datetime
    sunrise: datetime | None
    sunset: datetime | None
    day_length_hours: float | None
    always_above: bool | None


class AnnualSunResponse(BaseModel):
    """Evolución anual de las horas de sol para una ubicación."""

    latitude: float
    longitude: float
    year: int
    days: list[DailySun]


class SunPosition(BaseModel):
    """Posición del Sol (altitud/azimut) en un instante dado."""

    time: datetime
    altitude: float
    azimuth: float


class TrajectoryResponse(BaseModel):
    """Trayectoria del Sol a lo largo de un día, para una ubicación —
    base del gráfico polar del punto 3."""

    latitude: float
    longitude: float
    date: date
    samples: list[SunPosition]
