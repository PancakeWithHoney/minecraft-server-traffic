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
    gamemode: GamemodeProfile

"""Настройки сервера"""
@dataclass(frozen=True, slots=True)
class ServerProfile:
    base_sessions_per_hour: float
    max_players: int

"""Характеристики игрового режима"""
@dataclass(frozen=True, slots=True)
class GamemodeProfile:
    base_session_duration: float
    base_activity_coefficient: float
    base_messages_per_minute: float
    is_fixed_duration: bool = False

'''Общие настройки сессий (ограничения)'''
@dataclass(frozen=True, slots=True)
class SessionProfile:
    min_duration_seconds: int = 60
    max_duration_seconds: int = 3600 * 5

    min_activity: float = 0.0
    max_activity: float = 1.0

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