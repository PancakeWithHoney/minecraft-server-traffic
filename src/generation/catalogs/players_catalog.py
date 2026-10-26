"""Фабрика игроков (PlayerCatalog).

Строит список Player из параметров генерации (count, cities, rng).
Публичный контракт: players() + by_id() — чтобы reading_generator
не зависел от источника сущностей (сгенерированы или загружены из БД).
"""

from __future__ import annotations

import random

from src.models import Player, PlayerRole
from src.generation.player_names import generate_nickname


class PlayerCatalog:
    """Фабрика: строит count игроков из пула городов, детерминированно по rng."""

    def __init__(self, count: int, cities: list[str], rng: random.Random) -> None:
        if count <= 0:
            raise ValueError(f"count must be > 0, got {count}")
        if not cities:
            raise ValueError("cities must be non-empty")
        self._players = self._build(count, cities, rng)
        self._by_id = {p.id: p for p in self._players}

    # ---------- ФАБРИКА ----------
    def _build(self, count: int, cities: list[str], rng: random.Random) -> list[Player]:
        players: list[Player] = []
        used_nicks: set[str] = set()
        for i in range(count):
            players.append(Player(
                id=i,
                ip=self._random_ip(rng),
                nickname=self._unique_nick(used_nicks, rng),
                age=rng.randint(10, 25),
                role=self._random_role(rng),
                location=rng.choice(cities),
            ))
        return players

    # ---------- ПРИВАТНЫЕ ХЕЛПЕРЫ ----------
    @staticmethod
    def _random_ip(rng: random.Random) -> str:
        return (
            f"{rng.randint(1, 254)}.{rng.randint(0, 255)}."
            f"{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        )

    @staticmethod
    def _unique_nick(used: set[str], rng: random.Random) -> str:
        # generate_nickname принимает rng — см. правку player_names.py
        while True:
            nick = generate_nickname(rng)
            if nick not in used:
                used.add(nick)
                return nick

    @staticmethod
    def _random_role(rng: random.Random) -> PlayerRole:
        return rng.choices(
            population=[PlayerRole.DEFAULT, PlayerRole.VIP,
                        PlayerRole.MODERATOR, PlayerRole.ADMIN],
            weights=[90, 7, 2, 1],
            k=1,
        )[0]

    # ---------- ПУБЛИЧНЫЙ API ----------
    def players(self) -> list[Player]:
        return list(self._players)

    def by_id(self, player_id: int) -> Player | None:
        return self._by_id.get(player_id)
