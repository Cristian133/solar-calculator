"""Endpoints de `/sol` (ver docs/plan_tecnico.md, sección 5)."""

from fastapi import APIRouter, Query

from app.schemas.sol import AnnualSunResponse, DailySun
from app.solar.events import sunrise_sunset_year

router = APIRouter()


@router.get("/anual", response_model=AnnualSunResponse)
def anual(
    latitude: float = Query(..., ge=-90, le=90, description="Latitud del observador, en grados"),
    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Longitud del observador, en grados (positiva al este)",
    ),
    year: int = Query(..., ge=1, le=9999, description="Año calendario (gregoriano)"),
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
