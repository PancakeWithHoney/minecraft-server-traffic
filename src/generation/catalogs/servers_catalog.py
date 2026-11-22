"""Справочник серверов и их профилей.

- servers() — фабрика Server (count штук, детерминированно по rng).
- profile_for(server) — GamemodeProfile по server.game_mode.
- server_profile() — общий ServerProfile (base_sessions_per_hour, max_players).
"""

from __future__ import annotations

import random

from src.models import Server, GameModeType
from src.generation.metrics import ServerProfile, GamemodeProfile
from src.generation.profiles.gamemode_profiles import GAMEMODE_PROFILES


# Веса популярности режимов — для rng.choices (реалистичное распределение серверов)
_GAMEMODE_WEIGHTS: dict[GameModeType, int] = {
    GameModeType.SURVIVAL: 30,
    GameModeType.BEDWARS: 25,
    GameModeType.SKYWARS: 15,
    GameModeType.BUILD_BATTLE: 10,
    GameModeType.MURDER_MYSTERY: 8,
    GameModeType.HUNGER_GAMES: 7,
    GameModeType.TNT_RUN: 5,
    GameModeType.LOBBY: 20,
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
        weights = [_GAMEMODE_WEIGHTS.get(m, 1) for m in modes]
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
        return GAMEMODE_PROFILES[server.game_mode]

    def server_profile(self) -> ServerProfile:
        return self._server_profile