import random
from datetime import datetime

from src.generation.catalogs.servers_catalog import ServerCatalog
from src.generation.catalogs.players_catalog import PlayerCatalog
from src.generation.metrics import ServerProfile, SessionProfile
from src.generation.anomalies import AnomalyPolicy
from src.generation.activity import BatchGenerator

def _make_batch(seed: int = 42) -> BatchGenerator:
    servers = ServerCatalog(5, random.Random(seed), ServerProfile(100, 1000))
    players = PlayerCatalog(100, ["Moscow", "Kazan"], random.Random(seed))
    return BatchGenerator(
        servers, players, SessionProfile(),
        AnomalyPolicy(0.05, 3.0, random.Random(seed)), seed=seed,
    )

def test_generate_batch_returns_sessions():
    at = datetime(2024, 11, 17, 20, 0)
    sessions = _make_batch().generate_batch(at=at, size=5)
    assert len(sessions) == 5
    for s in sessions:
        assert s.player_id >= 0
        assert s.server_id >= 0
        assert s.duration_sec >= 0
        assert 0.0 <= s.activity_coefficient <= 1.0
        assert s.chat_messages_cnt >= 0
        assert s.ended_at >= s.started_at

def test_determinism():
    at = datetime(2024, 11, 17, 20, 0)
    d1 = [s.duration_sec for s in _make_batch(42).generate_batch(at, 5)]
    d2 = [s.duration_sec for s in _make_batch(42).generate_batch(at, 5)]
    assert d1 == d2