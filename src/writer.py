from __future__ import annotations

import logging
from typing import Any
from src.models import Player, Server
import clickhouse_connect
from clickhouse_connect.driver.client import Client

from src.models import SessionReading
from src.retry import RetryPolicy

logger = logging.getLogger(__name__)


class ClickHouseWriter:
    """Записывает сгенерированные сессии в ClickHouse батчами."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        retry_policy: RetryPolicy,
    ) -> None:
        self._client: Client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=user,
            password=password,
            database=database,
        )
        self._retry_policy = retry_policy

    def write_batch(self, sessions: list[SessionReading]) -> None:
        """Записывает пачку сессий с использованием retry-политики."""
        if not sessions:
            return

        # Формируем данные для вставки (без session_id, ClickHouse сам сгенерирует UUID)
        data = [
            (
                s.started_at,
                s.ended_at,
                s.player_id,
                s.server_id,
                s.exit_reason.value,  # Enum -> str
                s.chat_messages_cnt,
                s.activity_coefficient,
                s.duration_sec,
                int(s.is_anomaly),    # bool -> 0/1
            )
            for s in sessions
        ]

        columns = [
            "started_at", "ended_at", "player_id", "server_id",
            "exit_reason", "chat_messages_cnt", "activity_coefficient",
            "duration_sec", "is_anomaly"
        ]

        def _insert() -> None:
            self._client.insert(
                table="sessions",
                data=data,
                column_names=columns,
            )

        # Выполняем вставку через RetryPolicy
        self._retry_policy.execute(_insert)
        logger.info(f"Успешно записано {len(sessions)} сессий в ClickHouse.")

    def close(self) -> None:
        self._client.close()

    def write_players(self, players: list[Player]) -> None:
        """Записывает справочник игроков (вызывается один раз при старте)."""
        if not players:
            return
        data = [
            (p.id, p.ip, p.nickname, p.age, p.role.value, p.location)
            for p in players
        ]
        columns = ["id", "ip", "nickname", "age", "role", "location"]

        def _insert() -> None:
            self._client.insert(table="players", data=data, column_names=columns)

        self._retry_policy.execute(_insert)
        logger.info(f"Справочник игроков записан ({len(players)} шт).")

    def write_servers(self, servers: list[Server]) -> None:
        """Записывает справочник серверов (вызывается один раз при старте)."""
        if not servers:
            return
        data = [
            (s.id, s.name, s.ip, s.game_mode.value)
            for s in servers
        ]
        columns = ["id", "name", "ip", "game_mode"]

        def _insert() -> None:
            self._client.insert(table="servers", data=data, column_names=columns)

        self._retry_policy.execute(_insert)
        logger.info(f"Справочник серверов записан ({len(servers)} шт).")