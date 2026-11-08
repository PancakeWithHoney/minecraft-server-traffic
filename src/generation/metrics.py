from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import math

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

def _clamp(v: float, lo: float, hi: float) -> float:
    """Зажать в [lo, hi] — как в PDF."""
    return max(lo, min(hi, v))

class MetricSampler(ABC):
    @abstractmethod
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float: ...

class JoinTimeSampler(MetricSampler):
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        pass

class SessionDurationSampler(MetricSampler):
    def __init__(self, profile: SessionProfile) -> None:
        self._profile = profile           # ← глобальные min/max

    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        mode = ctx.gamemode               # ← параметры конкретного режима

        # ── 1. Фиксированная длительность (Build Battle, Murder Mystery) ──
        if mode.is_fixed_duration:
            return _clamp(
                mode.base_session_duration,
                self._profile.min_duration_seconds,
                self._profile.max_duration_seconds,
            )

        # ── 2. Переменная длительность (Survival, Bedwars) ──
        # 2.1. суточная сезонность: вечером дольше
        daily = (diurnal_factor(ctx.at) + 1.0) / 2.0    # 0..1
        daily_mult = 1.0 + 0.5 * daily                   # 1.0..1.5

        # 2.2. годовая сезонность: летом дольше
        yearly = (annual_factor(ctx.at) + 1.0) / 2.0    # 0..1
        yearly_mult = 1.0 + 0.3 * yearly                 # 1.0..1.3

        # 2.3. ожидаемая длительность
        expected = mode.base_session_duration * daily_mult * yearly_mult

        # 2.4. стохастика: логнормальное (тяжёлый хвост, как WindSpeed в PDF)
        mu = math.log(max(expected, 1.0))
        value = rng.lognormvariate(mu, 0.7)

        # 2.5. clamp в глобальные границы
        return round(_clamp(
            value,
            self._profile.min_duration_seconds,
            self._profile.max_duration_seconds,
        ), 1)

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