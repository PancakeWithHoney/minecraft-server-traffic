
from __future__ import annotations
import enum
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Player:
    id: int
    nickname: str
    age: int
    role: str
    location: str

@dataclass
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

class ActionType(enum.Enum):
    JOIN = "join"
    LEAVE = "leave"

class ExitReason(enum.Enum):
    DEFAULT = "default"
    TIMEOUT = "timeout"
    SERVER_NOT_RESPONDING = "server_not_responding"
    KICK = "kick"
    BAN = "ban"
    UNKNOWN = "unknown"