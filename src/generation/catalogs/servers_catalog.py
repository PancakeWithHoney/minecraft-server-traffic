"""Справочник серверов и их профилей.

- servers() — фабрика Server (count штук, детерминированно по rng).
- profile_for(server) — GamemodeProfile по server.game_mode.
- server_profile() — общий ServerProfile (base_sessions_per_hour, max_players).
"""

import random

from __future__ import annotations

from dataclasses import dataclass

from src.models import Server, GameModeType

from ..metrics import ServerProfile, GamemodeProfile
from ..profiles.gamemode_profiles import GAMEMODE_PROFILES

"""Справочник серверов и их профилей активности
"""

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
    server_profile: ServerProfile

_TEMPLATES: dict[str, _Template] = {
    "surv_1": _Template(
        "EPIC SURVIVAL 1000LVL",
        GameModeType.SURVIVAL,
        ServerProfile(
            base_sessions_per_hour=100,
            max_players=1000,
        )
    ),
    "surv_2": _Template(
        "HARDCORE SURVIVAL",
        GameModeType.SURVIVAL,
        ServerProfile(
            base_sessions_per_hour=20,
            max_players=1000,
        )
    ),
    "bedwars_1": _Template(
        "BEDWARS",
        GameModeType.BEDWARS,
        ServerProfile(
            base_sessions_per_hour=100,
            max_players=30,
        )
    ),
    "buildbattle": _Template(
        "LEGENDARY BUILD BATTLE",
        GameModeType.BUILD_BATTLE,
        ServerProfile(
            base_sessions_per_hour=50,
            max_players=10,
        )
    ),
    "murdermystery": _Template(
        "MYRDER MYSTERY",
        GameModeType.MURDER_MYSTERY,
        ServerProfile(
            base_sessions_per_hour=100,
            max_players=30,
        )
    ),
    "skywars": _Template(
        "EPIC SKYWARS",
        GameModeType.SKYWARS,
        ServerProfile(
            base_sessions_per_hour=120,
            max_players=30,
        )
    ),
    "lobby": _Template(
        "WONDERFUL LOBBY",
        GameModeType.LOBBY,
        ServerProfile(
            base_sessions_per_hour=1000,
            max_players=2000,
        )
    ),
    "hunger": _Template(
        "HUNGER GAMES ",
        GameModeType.LOBBY,
        ServerProfile(
            base_sessions_per_hour=70,
            max_players=30,
        )
    ),
}


class ServerCatalog:
    """Фабрика серверов: count штук, детерминированно по rng."""

    def __init__(
        self,
        count: int,
        rng: random.Random,
        server_profile: ServerProfile,
    ) -> None:
        if count <= 0:
            raise ValueError(f"count must be > 0, got {count}")
        self._server_profile = server_profile
        self._servers = self._build(count, rng)
        self._by_id = {s.id: s for s in self._servers}

    # ---------- ФАБРИКА ----------
    def _build(self, count: int, rng: random.Random) -> list[Server]:
        modes = list(GAMEMODE_PROFILES.keys())
        weights = [_GAMEMODE_WEIGHTS[m] for m in modes]
        servers: list[Server] = []
        for i in range(count):
            mode = rng.choices(modes, weights=weights, k=1)[0]
            servers.append(Server(
                id=i,
                name=f"server_{i}_{mode.value}",
                ip=self._random_ip(rng),
                game_mode=mode,
            ))
        return servers

    @staticmethod
    def _random_ip(rng: random.Random) -> str:
        return (
            f"10.{rng.randint(0, 255)}."
            f"{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        )

    # ---------- ПУБЛИЧНЫЙ API ----------
    def servers(self) -> list[Server]:
        return list(self._servers)

    def by_id(self, server_id: int) -> Server | None:
        return self._by_id.get(server_id)

    # ---------- МОСТ К СЭМПЛЕРАМ ----------
    def profile_for(self, server: Server) -> GamemodeProfile:
        """GamemodeProfile по режиму сервера — аналог climate_for(station)."""
        return _GAMEMODE_PROFILES[server.game_mode]

    def server_profile(self) -> ServerProfile:
        """Общий ServerProfile (base_sessions_per_hour, max_players)."""
        return self._server_profile