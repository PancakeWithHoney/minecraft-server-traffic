from __future__ import annotations

import random
from datetime import datetime, timedelta

from src.models import Server, ExitReason, SessionReading
from src.generation.metrics import (
    ReadingContext, GamemodeProfile, ServerProfile, SessionProfile,
    SessionDurationSampler, ActivityCoefficientSampler, MessagesCountSampler
)
from src.generation.anomalies import AnomalyKind, AnomalyPolicy
from src.generation.catalogs.players_catalog import PlayerCatalog
from src.generation.catalogs.servers_catalog import ServerCatalog


class _ExitReasonPicker:
    def pick(self, ctx: ReadingContext, duration: float, anomaly: AnomalyKind | None, rng: random.Random) -> ExitReason:
        if anomaly == AnomalyKind.SHORT_SESSIONS:
            return ExitReason.TIMEOUT
        if rng.random() < 0.02:
            return ExitReason.SERVER_NOT_RESPONDING
        return ExitReason.DEFAULT


class SessionReadingGenerator:
    def __init__(
        self,
        server: Server,
        gamemode_profile: GamemodeProfile,
        session_profile: SessionProfile,
        server_profile: ServerProfile,
        anomaly_policy: AnomalyPolicy,
        rng: random.Random,
        players: PlayerCatalog,
    ) -> None:
        self._server = server
        self._gamemode_profile = gamemode_profile
        self._server_profile = server_profile
        self._rng = rng
        self._anomaly_policy = anomaly_policy
        self._players = players

        self._duration = SessionDurationSampler(session_profile)
        self._activity = ActivityCoefficientSampler(session_profile)
        self._messages = MessagesCountSampler()
        self._exit_picker = _ExitReasonPicker()

    @property
    def server(self) -> Server:
        return self._server

    def generate(self, at: datetime) -> SessionReading:
        anomaly = self._anomaly_policy.decide()
        rng = self._rng
        player = self._players.random_player(rng)

        # Фаза 1: генерация длительности
        ctx = ReadingContext(
            at=at,
            gamemode=self._gamemode_profile,
            server=self._server_profile,
            duration_seconds=0.0,
        )
        duration = self._duration.sample(ctx, rng)
        duration = self._apply_duration_anomaly(duration, anomaly)

        # Фаза 2: пересборка ctx с реальной длительностью для остальных метрик
        ctx = ReadingContext(
            at=at,
            gamemode=self._gamemode_profile,
            server=self._server_profile,
            duration_seconds=duration,
        )
        activity = self._activity.sample(ctx, rng)
        messages = self._messages.sample(ctx, rng)
        exit_reason = self._exit_picker.pick(ctx, duration, anomaly, rng)

        return SessionReading(
            session_id=0,
            started_at=at,
            ended_at=at + timedelta(seconds=duration),
            player_id=player.id,
            server_id=self._server.id,
            exit_reason=exit_reason,
            chat_messages_cnt=int(messages),
            activity_coefficient=activity,
            duration_sec=float(duration),
            is_anomaly=anomaly is not None,
        )

    def _apply_duration_anomaly(self, value: float, anomaly: AnomalyKind | None) -> float:
        strength = self._anomaly_policy.strength
        if anomaly == AnomalyKind.LONG_SESSIONS:
            return round(value * strength * self._rng.uniform(1.5, 2.5), 1)
        if anomaly == AnomalyKind.SHORT_SESSIONS:
            return round(max(10.0, value / strength / self._rng.uniform(1.5, 2.5)), 1)
        return value


class BatchGenerator:
    def __init__(
        self,
        servers_catalog: ServerCatalog,
        players_catalog: PlayerCatalog,
        session_profile: SessionProfile,
        anomaly_policy: AnomalyPolicy,
        seed: int,
    ) -> None:
        rng = random.Random(seed)
        self._per_server = [
            SessionReadingGenerator(
                server=s,
                gamemode_profile=servers_catalog.profile_for(s),
                session_profile=session_profile,
                server_profile=servers_catalog.server_profile(),
                anomaly_policy=anomaly_policy,
                rng=rng,
                players=players_catalog,
            )
            for s in servers_catalog.servers()
        ]

    @property
    def servers(self) -> list[Server]:
        return [g.server for g in self._per_server]

    def generate_batch(self, at: datetime, size: int) -> list[SessionReading]:
        if not self._per_server:
            return []
        sessions: list[SessionReading] = []
        for index in range(size):
            generator = self._per_server[index % len(self._per_server)]
            sessions.append(generator.generate(at))
        return sessions