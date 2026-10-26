"""Справочник серверов и их профилей активности
"""

from __future__ import annotations

from dataclasses import dataclass

from src.models import Server, GameModeType

from ..metrics import GamemodeProfile

_GENERIC = GamemodeProfile(
    gamemode=GameModeType.SURVIVAL,
    max_players=1000,
    base_sessions_per_hour=100,
    base_activity_coefficient=1.0,
    base_messages_per_minute=10
)


@dataclass(frozen=True, slots=True)
class _Template:
    server_name: str
    gamemode: str

_TEMPLATES: dict[str, _Template] = {
    "surv_1": _Template(
        "EPIC_SURVIVAL_1000LVL",
        GamemodeProfile(

        )
    ),
    "Moscow": _Template(
        "Moscow", 55.76, 37.62, 156,
        ClimateProfile(mean_annual_temp_c=6.0, annual_temp_amplitude_c=25.0,
                       daily_temp_amplitude_c=7.0, humidity_base_pct=72.0,
                       pressure_base_hpa=1013.0, wind_base_ms=5.0),
    ),
    "Kazan": _Template(
        "Kazan", 55.79, 49.12, 64,
        ClimateProfile(mean_annual_temp_c=4.5, annual_temp_amplitude_c=27.0,
                       daily_temp_amplitude_c=7.0, humidity_base_pct=73.0,
                       pressure_base_hpa=1013.0, wind_base_ms=4.5),
    ),
    "Sochi": _Template(
        "Sochi", 43.60, 39.73, 30,
        ClimateProfile(mean_annual_temp_c=14.0, annual_temp_amplitude_c=14.0,
                       daily_temp_amplitude_c=6.0, humidity_base_pct=75.0,
                       pressure_base_hpa=1012.0, wind_base_ms=3.0),
    ),
    "Irkutsk": _Template(
        "Irkutsk", 52.29, 104.28, 444,
        ClimateProfile(mean_annual_temp_c=1.0, annual_temp_amplitude_c=33.0,
                       daily_temp_amplitude_c=9.0, humidity_base_pct=68.0,
                       pressure_base_hpa=1005.0, wind_base_ms=4.0),
    ),
}


class StationCatalog:
    """Фабрика станций по списку городов из конфигурации."""

    def __init__(self, cities: list[str]) -> None:
        self._templates = [self._resolve(city) for city in cities]

    @staticmethod
    def _resolve(city: str) -> _Template:
        # Неизвестный город получает обобщённый профиль, чтобы система не падала.
        return _TEMPLATES.get(city, _Template(city, 0.0, 0.0, 100.0, _GENERIC))

    def stations(self) -> list[Station]:
        return [
            Station(
                station_id=index,
                name=f"{t.city} Station",
                city=t.city,
                latitude=t.latitude,
                longitude=t.longitude,
                altitude=t.altitude,
            )
            for index, t in enumerate(self._templates)
        ]

    def climate_for(self, station: Station) -> ClimateProfile:
        return next(t.climate for t in self._templates if t.city == station.city)