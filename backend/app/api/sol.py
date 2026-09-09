"""Endpoints de `/sol` (ver docs/plan_tecnico.md, sección 5)."""

from datetime import date as date_type
from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.sol import AnnualSunResponse, DailySun, SunPosition, TrajectoryResponse
from app.solar.events import sun_trajectory, sunrise_sunset_year

router = APIRouter()

_MIN_TRAJECTORY_SAMPLES = 24
_MAX_TRAJECTORY_SAMPLES = 288

Latitude = Annotated[float, Query(ge=-90, le=90, description="Latitud del observador, en grados")]
Longitude = Annotated[
    float,
    Query(ge=-180, le=180, description="Longitud del observador, en grados (positiva al este)"),
]


@router.get("/anual", response_model=AnnualSunResponse)
def anual(
    latitude: Latitude,
    longitude: Longitude,
    year: Annotated[int, Query(ge=1, le=9999, description="Año calendario (gregoriano)")],
) -> AnnualSunResponse:
    """Evolución anual de las horas de sol (punto 2) para una ubicación
    dada — orto, tránsito, ocaso y duración del día para cada día del año.
    """
    result = sunrise_sunset_year(year, latitude, longitude)

    days = [
        DailySun(
            date=day,
            transit=transit,
            sunrise=sunrise,
            sunset=sunset,
            day_length_hours=(
                (sunset - sunrise).total_seconds() / 3600 if sunrise and sunset else None
            ),
            always_above=always_above,
        )
        for day, transit, sunrise, sunset, always_above in zip(
            result.dates,
            result.transit,
            result.sunrise,
            result.sunset,
            result.always_above,
            strict=True,
        )
    ]

    return AnnualSunResponse(latitude=latitude, longitude=longitude, year=year, days=days)


@router.get("/trayectoria", response_model=TrajectoryResponse)
def trayectoria(
    latitude: Latitude,
    longitude: Longitude,
    date: Annotated[date_type, Query(description="Fecha (UTC)")],
    num_samples: Annotated[
        int,
        Query(
            ge=_MIN_TRAJECTORY_SAMPLES,
            le=_MAX_TRAJECTORY_SAMPLES,
            description="Cantidad de instantes a muestrear a lo largo del día (equiespaciados)",
        ),
    ] = 96,
) -> TrajectoryResponse:
    """Trayectoria del Sol (altitud/azimut) a lo largo de un día (punto 3),
    para un gráfico polar. Incluye las 24h del día, no solo las horas de
    luz — el cliente filtra por altitud si solo quiere el tramo diurno.
    """
    result = sun_trajectory(date, latitude, longitude, num_samples)

    samples = [
        SunPosition(time=time, altitude=alt, azimuth=az)
        for time, alt, az in zip(result.times, result.altitude, result.azimuth, strict=True)
    ]

    return TrajectoryResponse(latitude=latitude, longitude=longitude, date=date, samples=samples)
