
from __future__ import annotations
import enum
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class Player:
    id: int
    ip: str
    nickname: str
    age: int
    role: PlayerRole
    location: str

class PlayerRole(enum.StrEnum):
    DEFAULT = "default"
    VIP = "vip"
    MODERATOR = "moderator"
    ADMIN = "admin"

@dataclass(frozen=True, slots=True)
class Server:
    id: int
    name: str
    ip: str
    game_mode: GameModeType


class GameModeType(enum.StrEnum):
    SURVIVAL = "survival"
    BEDWARS = "creative"
    SKYWARS = 'skywars'
    BUILD_BATTLE = 'buildbattle'
    MURDER_MYSTERY = 'murdermystery'
    HUNGER_GAMES = 'hungergames'
    TNT_RUN = 'tntrun'


class ExitReason(enum.StrEnum):
    DEFAULT = "default"
    TIMEOUT = "timeout"
    SERVER_NOT_RESPONDING = "server_not_responding"
    KICK = "kick"
    BAN = "ban"

@dataclass(frozen=True, slots=True)
class SessionReading:
    session_id: int
    started_at: datetime
    player_id: int
    server_id: int
    exit_reason: ExitReason
    chat_messages_cnt: int
    activity_coefficient: float
    duration_sec: int
    is_anomaly: bool