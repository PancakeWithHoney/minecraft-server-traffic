from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import math

from src.generation.distributions import poisson
from seasonality import diurnal_factor, annual_factor

@dataclass(frozen=True)
class ReadingContext:
    at: datetime
    gamemode: GamemodeProfile
    server: ServerProfile
    duration_seconds: float # длительность одной сессии, необходима для генерации кол-ва сообщений

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
    return max(lo, min(hi, v))

class MetricSampler(ABC):
    @abstractmethod
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float: ...

class JoinTimeSampler(MetricSampler):
    def sample(self, ctx: ReadingContext, rng: random.Random) -> float:
        """Генерирует количество секунд до следующего входа"""
        sessions_per_hour = ctx.server.base_sessions_per_hour

        if sessions_per_hour <= 0:
            raise ValueError("base_sessions_per_hour должен быть больше 0")

        # Суточная сезонность
        daily = (diurnal_factor(ctx.at) + 1.0) / 2.0
        daily_mult = 1.0 + 0.5 * daily

        # Годовая сезонность
        yearly = (annual_factor(ctx.at) + 1.0) / 2.0
        yearly_mult = 1.0 + 0.3 * yearly

        # Интенсивность входов с учётом сезонности
        rate_per_hour = (
            sessions_per_hour * daily_mult * yearly_mult
        )

        # Переводим интенсивность в секунды
        rate_per_second = rate_per_hour / 3600

        # Случайный интервал до следующего входа
        return rng.expovariate(rate_per_second)

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

        # ── 2. Переменная длительность ──
        # 2.1. суточная сезонность
        daily = (diurnal_factor(ctx.at) + 1.0) / 2.0
        daily_mult = 1.0 + 0.5 * daily

        # 2.2. годовая сезонность
        yearly = (annual_factor(ctx.at) + 1.0) / 2.0
        yearly_mult = 1.0 + 0.3 * yearly

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
        mean = ctx.gamemode.base_activity_coefficient

        mean = _clamp(
            mean,
            self._profile.min_activity,
            self._profile.max_activity,
        )

        if mean <= 0.0 or mean >= 1.0:
            return mean

        # Чем больше concentration, тем меньше разброс
        concentration = 12.0

        alpha = mean * concentration
        beta = (1.0 - mean) * concentration

        value = rng.betavariate(alpha, beta)

        return _clamp(
            value,
            self._profile.min_activity,
            self._profile.max_activity,
        )

class MessagesCountSampler(MetricSampler):
    def sample(self, ctx: ReadingContext, rng: random.Random) -> int:
        duration_minutes = ctx.duration_seconds / 60

        lam = (
            ctx.gamemode.base_messages_per_minute
            * duration_minutes
        )

        return poisson(lam, rng)