from __future__ import annotations

import logging
import random
import signal
import sys
import time
from datetime import datetime

from src.config import get_settings
from src.retry import RetryPolicy
from src.writer import ClickHouseWriter
from src.generation.anomalies import AnomalyPolicy
from src.generation.metrics import ServerProfile, SessionProfile
from src.generation.catalogs.players_catalog import PlayerCatalog
from src.generation.catalogs.servers_catalog import ServerCatalog
from src.generation.activity import BatchGenerator

logger = logging.getLogger(__name__)

# Флаг для graceful shutdown
stop_event = False


def handle_shutdown(signum, frame):
    global stop_event
    logger.info("Получен сигнал завершения. Останавливаем генератор...")
    stop_event = True


def main() -> None:
    # 1. Настройка логирования
    settings = get_settings()
    logging.basicConfig(
        level=settings.generator.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.info("Запуск генератора Minecraft Server Traffic...")

    # Обработка Ctrl+C и сигнала остановки от Docker
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # 2. Инициализация RNG и каталогов
    # Используем разные сиды, чтобы игроки и серверы не коррелировали
    rng_players = random.Random(settings.generator.seed)
    rng_servers = random.Random(settings.generator.seed + 1)
    rng_generator = random.Random(settings.generator.seed + 2)
    rng_anomaly = random.Random(settings.generator.seed + 3)

    logger.info("Инициализация каталогов...")
    player_catalog = PlayerCatalog(
        count=settings.generator.player_count,
        cities=settings.generator.city_list,
        rng=rng_players,
    )
    # Серверов у нас 10, и мы задаем общий профиль (например, до 1000 игроков)
    server_profile = ServerProfile(base_sessions_per_hour=100, max_players=1000)
    server_catalog = ServerCatalog(
        count=settings.generator.server_count,
        rng=rng_servers,
        server_profile=server_profile,
    )

    # 3. Инициализация генератора
    anomaly_policy = AnomalyPolicy(
        probability=settings.generator.anomaly_probability,
        strength=settings.generator.anomaly_strength,
        rng=rng_anomaly,
    )
    batch_generator = BatchGenerator(
        servers_catalog=server_catalog,
        players_catalog=player_catalog,
        session_profile=SessionProfile(),
        anomaly_policy=anomaly_policy,
        seed=settings.generator.seed + 4,
    )

    # 4. Инициализация записи в БД
    retry_policy = RetryPolicy(
        max_attempts=settings.generator.retry_max_attempts,
        base_delay=settings.generator.retry_base_delay_seconds,
        max_delay=settings.generator.retry_max_delay_seconds,
        backoff_factor=settings.generator.retry_backoff_factor,
    )

    logger.info("Подключение к ClickHouse...")
    writer = ClickHouseWriter(
        host=settings.clickhouse.host,
        port=settings.clickhouse.port,
        user=settings.clickhouse.user,
        password=settings.clickhouse.password,
        database=settings.clickhouse.database,
        retry_policy=retry_policy,
    )

    # 5. Записываем справочники ОДИН РАЗ при старте
    logger.info("Запись справочников в БД...")
    writer.write_players(player_catalog.players())
    writer.write_servers(server_catalog.servers())

    # 6. Главный цикл сервиса
    logger.info(
        f"Старт генерации. Батч: {settings.generator.batch_size}, Интервал: {settings.generator.interval_seconds} сек.")

    try:
        while not stop_event:
            current_time = datetime.now()

            # Генерируем пачку сессий
            sessions = batch_generator.generate_batch(
                at=current_time,
                size=settings.generator.batch_size,
            )

            # Пишем в БД
            writer.write_batch(sessions)

            # Ждем до следующего батча (но с проверкой stop_event, чтобы быстро выйти при Ctrl+C)
            for _ in range(int(settings.generator.interval_seconds * 10)):
                if stop_event:
                    break
                time.sleep(0.1)

    except Exception as e:
        logger.exception("Критическая ошибка в главном цикле:")
    finally:
        # Graceful shutdown
        logger.info("Завершение работы генератора. Закрываем соединение с БД...")
        writer.close()
        logger.info("Генератор успешно остановлен.")


if __name__ == "__main__":
    main()