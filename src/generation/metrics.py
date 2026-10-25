from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from src.models import GameModeType
from seasonality import diurnal_factor, annual_factor

@dataclass(frozen=True)
class ReadingContext:
    at: datetime
    server: ServerProfile
    current_online: int

"""Настройки сервера"""
@dataclass(frozen=True)
class ServerProfile:
    gamemode: GameModeType
    max_players: int
    average_online: int

@dataclass(frozen=True, slots=True)
class SessionProfile:
    min_duration_seconds: int = 60
    max_duration_seconds: int = 3600 * 5
    typical_duration_seconds: int = 20 * 60

class MetricSampler(ABC):
    @abstractmethod
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float: ...

class JoinTimeSampler(MetricSampler):
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        pass

class SessionDurationSampler(MetricSampler):
    def __init__(self, profile: SessionProfile) -> None:
        self._profile = profile

    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        pass

class ActivityCoefficientSampler(MetricSampler):
    def __init__(self, profile: SessionProfile) -> None:
        self._profile = profile

    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        pass

class MessagesCountSampler(MetricSampler):
    def __init__(self, profile: SessionProfile) -> None:
        self._profile = profile

    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        pass