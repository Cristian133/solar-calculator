"""Endpoints de `/sol` (ver docs/plan_tecnico.md, sección 5)."""

from datetime import date as date_type
from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.sol import (
    AnnualSunResponse,
    DailySun,
    DailySunResponse,
    IrradianceResponse,
    IrradianceSample,
    SolarNoonResponse,
    SunPosition,
    TrajectoryResponse,
)
from app.solar.events import (
    daily_irradiation,
    solar_noon,
    sun_trajectory,
    sunrise_sunset,
    sunrise_sunset_year,
)

router = APIRouter()

_MIN_SAMPLES = 24
_MAX_SAMPLES = 288

Latitude = Annotated[float, Query(ge=-90, le=90, description="Latitud del observador, en grados")]
Longitude = Annotated[
    float,
    Query(ge=-180, le=180, description="Longitud del observador, en grados (positiva al este)"),
]
DateParam = Annotated[date_type, Query(description="Fecha (UTC)")]
NumSamples = Annotated[
    int,
    Query(
        ge=_MIN_SAMPLES,
        le=_MAX_SAMPLES,
        description="Cantidad de instantes a muestrear a lo largo del día (equiespaciados)",
    ),
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


@router.get("/dia", response_model=DailySunResponse)
def dia(latitude: Latitude, longitude: Longitude, date: DateParam) -> DailySunResponse:
    """Horas de sol en un día (punto 1): orto, tránsito, ocaso y duración
    del día para una ubicación y fecha dadas."""
    result = sunrise_sunset(date, latitude, longitude)
    day_length_hours = (
        (result.sunset - result.sunrise).total_seconds() / 3600
        if result.sunrise and result.sunset
        else None
    )
    return DailySunResponse(
        latitude=latitude,
        longitude=longitude,
        date=date,
        transit=result.transit,
        sunrise=result.sunrise,
        sunset=result.sunset,
        day_length_hours=day_length_hours,
        always_above=result.always_above,
    )


@router.get("/mediodia", response_model=SolarNoonResponse)
def mediodia(latitude: Latitude, longitude: Longitude, date: DateParam) -> SolarNoonResponse:
    """Mediodía solar e inclinación del Sol en ese instante (punto 4):
    altitud máxima del día y azimut (0°=Norte o 180°=Sur)."""
    result = solar_noon(date, latitude, longitude)
    return SolarNoonResponse(
        latitude=latitude,
        longitude=longitude,
        date=date,
        transit=result.transit,
        altitude_deg=result.altitude_deg,
        azimuth_deg=result.azimuth_deg,
    )


@router.get("/trayectoria", response_model=TrajectoryResponse)
def trayectoria(
    latitude: Latitude,
    longitude: Longitude,
    date: DateParam,
    num_samples: NumSamples = 96,
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


@router.get("/irradiancia", response_model=IrradianceResponse)
def irradiancia(
    latitude: Latitude,
    longitude: Longitude,
    date: DateParam,
    num_samples: NumSamples = 96,
) -> IrradianceResponse:
    """Irradiancia solar en cielo despejado a lo largo de un día (punto 5)
    y la energía total recibida por m² en el día. Modelo teórico
    simplificado (ver `app.solar.irradiance`): no tiene en cuenta nubosidad
    real ni componente difusa.
    """
    result = daily_irradiation(date, latitude, longitude, num_samples)

    samples = [
        IrradianceSample(time=time, power_w_per_m2=power)
        for time, power in zip(result.times, result.power_w_per_m2, strict=True)
    ]

    return IrradianceResponse(
        latitude=latitude,
        longitude=longitude,
        date=date,
        energy_wh_per_m2=result.energy_wh_per_m2,
        samples=samples,
    )
