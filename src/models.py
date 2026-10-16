
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

class ActionType(enum.StrEnum):
    JOIN = "join"
    LEAVE = "leave"

class ExitReason(enum.StrEnum):
    DEFAULT = "default"
    TIMEOUT = "timeout"
    SERVER_NOT_RESPONDING = "server_not_responding"
    KICK = "kick"
    BAN = "ban"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class PlayerReading:
    id: int
    timestamp: datetime
    player_id: int
    server_id: int
    action_type: ActionType
    exit_reason: ExitReason | None
    is_anomaly: bool