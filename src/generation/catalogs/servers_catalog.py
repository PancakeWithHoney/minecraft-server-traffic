"""Справочник серверов и их профилей.

- servers() — фабрика Server (count штук, детерминированно по rng).
- profile_for(server) — GamemodeProfile по server.game_mode.
- server_profile() — общий ServerProfile (base_sessions_per_hour, max_players).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.models import Server, GameModeType
from src.metrics import GamemodeProfile, ServerProfile


# ─────────────────────────────────────────────────────────────
# Шаблоны профилей режимов (аналог _TEMPLATES в weather, но
# это не сущности, а параметры — поэтому отдельно от _build)
# ─────────────────────────────────────────────────────────────
_GAMEMODE_PROFILES: dict[GameModeType, GamemodeProfile] = {
    GameModeType.SURVIVAL: GamemodeProfile(
        base_session_duration=1800.0,        # 30 мин
        base_activity_coefficient=0.7,
        base_messages_per_minute=2.0,
        is_fixed_duration=False,
    ),
    GameModeType.BEDWARS: GamemodeProfile(
        base_session_duration=900.0,         # 15 мин
        base_activity_coefficient=0.9,
        base_messages_per_minute=3.0,
        is_fixed_duration=False,
    ),
    GameModeType.SKYWARS: GamemodeProfile(
        base_session_duration=720.0,         # 12 мин
        base_activity_coefficient=0.85,
        base_messages_per_minute=3.0,
        is_fixed_duration=False,
    ),
    GameModeType.BUILD_BATTLE: GamemodeProfile(
        base_session_duration=600.0,         # 10 мин — фикс
        base_activity_coefficient=0.6,
        base_messages_per_minute=5.0,
        is_fixed_duration=True,
    ),
    GameModeType.MURDER_MYSTERY: GamemodeProfile(
        base_session_duration=540.0,         # 9 мин — фикс
        base_activity_coefficient=0.7,
        base_messages_per_minute=4.0,
        is_fixed_duration=True,
    ),
    GameModeType.HUNGER_GAMES: GamemodeProfile(
        base_session_duration=1500.0,        # 25 мин
        base_activity_coefficient=0.8,
        base_messages_per_minute=2.5,
        is_fixed_duration=False,
    ),
    GameModeType.TNT_RUN: GamemodeProfile(
        base_session_duration=300.0,         # 5 мин — фикс
        base_activity_coefficient=0.95,
        base_messages_per_minute=2.0,
        is_fixed_duration=True,
    ),
}

# Веса популярности режимов — для rng.choices
_GAMEMODE_WEIGHTS: dict[GameModeType, int] = {
    GameModeType.SURVIVAL: 30,
    GameModeType.BEDWARS: 25,
    GameModeType.SKYWARS: 15,
    GameModeType.BUILD_BATTLE: 10,
    GameModeType.MURDER_MYSTERY: 8,
    GameModeType.HUNGER_GAMES: 7,
    GameModeType.TNT_RUN: 5,
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
        modes = list(_GAMEMODE_PROFILES.keys())
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