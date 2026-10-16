import enum
from __future__ import annotations

import enum
import random

class AnomalyKind(enum.StrEnum):
    MASS_JOIN = "mass_join"
    MASS_LEAVE = "mass_leave"
    RAPID_RECONNECT = "rapid_reconnect"
    SHORT_SESSIONS = "short_sessions"
    LONG_SESSIONS = "long_sessions"

class AnomalyPolicy:
        """Решает, случится ли аномалия в текущем показании и какая именно."""
        def __init__(self, probability: float, strength: float, rng: random.Random) -> None:
            self._probability = probability
            self._strength = strength
            self._rng = rng

        @property
        def strength(self) -> float:
            """Сила аномалии (множитель), настраивается извне."""
            return self._strength

        def decide(self) -> AnomalyKind | None:
            """Возвращает тип аномалии для текущей записи или ``None``."""
            if self._rng.random() >= self._probability:
                return None
            return self._rng.choice(list(AnomalyKind))