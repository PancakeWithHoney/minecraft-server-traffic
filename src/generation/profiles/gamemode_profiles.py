from src.generation.metrics import GamemodeProfile
from src.models import GameModeType

GAMEMODE_PROFILES = {
    GameModeType.TNT_RUN: GamemodeProfile(
        base_session_duration=60 * 5,
        base_activity_coefficient=0.95,
        base_messages_per_minute=0.02,
    ),
    GameModeType.BEDWARS: GamemodeProfile(
        base_session_duration=60 * 20,
        base_activity_coefficient=0.75,
        base_messages_per_minute=0.15,
    ),
    GameModeType.SURVIVAL: GamemodeProfile(
        base_session_duration=60 * 60,
        base_activity_coefficient=0.55,
        base_messages_per_minute=0.08,
    ),
    GameModeType.HUNGER_GAMES: GamemodeProfile(
        base_session_duration=60 * 15,
        base_activity_coefficient=0.85,
        base_messages_per_minute=0.08,
    ),
    GameModeType.LOBBY: GamemodeProfile(
        base_session_duration=60 * 3,
        base_activity_coefficient=0.1,
        base_messages_per_minute=0.12,
    ),
    GameModeType.BUILD_BATTLE: GamemodeProfile(
        base_session_duration=60 * 12,
        base_activity_coefficient=0.7,
        base_messages_per_minute=0.12,
        is_fixed_duration=True
    ),
    GameModeType.MURDER_MYSTERY: GamemodeProfile(
        base_session_duration=60 * 12,
        base_activity_coefficient=0.5,
        base_messages_per_minute=0.08,
    ),
    GameModeType.SKYWARS: GamemodeProfile(
        base_session_duration=60 * 12,
        base_activity_coefficient=0.85,
        base_messages_per_minute=0.08,
    ),
}



