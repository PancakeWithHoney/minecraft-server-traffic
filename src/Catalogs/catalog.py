from __future__ import annotations
from dataclasses import dataclass
from generator.models import Station
from .metrics import ClimateProfile

_GENERIC = ClimateProfile(
mean_annual_temp_c=10.0,
annual_temp_amplitude_c=20.0,
daily_temp_amplitude_c=7.0,
humidity_base_pct=70.0,
)

@dataclass(frozen=True, slots=True)
class _Template:
    city: str
    latitude: float
    longitude: float
    altitude: float
    climate: ClimateProfile

_TEMPLATES: dict[str, _Template] = {
"Vladivostok": _Template("Vladivostok", 43.12, 131.89, 40, ClimateProfile(...)),
"Moscow": _Template("Moscow", 55.76, 37.62, 156, ClimateProfile(...)),
"Kazan": ..., "Sochi": ..., "Irkutsk": ...,
}



class PlayerCatalog:
    def __init__(self, count: int, cities: list[str], rng: random.Random) -> None:
        self._players = self._build(count, cities, rng)
        self._by_id = {p.id: p for p in self._players}

    def _build(self, count, cities, rng) -> list[Player]:
        players = []
        used_nicks: set[str] = set()
        for i in range(count):
            players.append(Player(
                id=i,
                ip=self._random_ip(rng),
                nickname=self._unique_nick(used_nicks),
                age=rng.randint(10, 25),
                role=self._random_role(rng),
                location=rng.choice(cities),
            ))
        return players

    def players(self) -> list[Player]:
        return list(self._players)

    def by_id(self, player_id: int) -> Player | None:
        return self._by_id.get(player_id)


