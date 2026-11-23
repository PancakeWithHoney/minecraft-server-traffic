-- init.sql
CREATE DATABASE IF NOT EXISTS gaming;

-- Таблица фактов (Сессии)
CREATE TABLE IF NOT EXISTS gaming.sessions (
    session_id UUID DEFAULT generateUUIDv4(),
    started_at DateTime,
    ended_at DateTime,
    player_id UInt32,
    server_id UInt32,
    exit_reason LowCardinality(String),
    chat_messages_cnt UInt32,
    activity_coefficient Float32,
    duration_sec Float32,
    is_anomaly UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(started_at)
ORDER BY (started_at, server_id);

-- Справочник серверов
CREATE TABLE IF NOT EXISTS gaming.servers (
    id UInt32,
    name String,
    ip String,
    game_mode LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY id;

-- Справочник игроков
CREATE TABLE IF NOT EXISTS gaming.players (
    id UInt32,
    ip String,
    nickname String,
    age UInt8,
    role LowCardinality(String),
    location LowCardinality(String)
) ENGINE = MergeTree()
ORDER BY id;

-- Materialized View для real-time аналитики (ТЗ)
-- Считает статистику по игровым режимам каждый час
-- Materialized View для real-time аналитики (ТЗ)
CREATE MATERIALIZED VIEW IF NOT EXISTS gaming.mv_hourly_stats
ENGINE = SummingMergeTree()
ORDER BY (hour, server_id)
AS SELECT
    toStartOfHour(started_at) AS hour,
    server_id,
    count() AS session_count,
    sum(duration_sec) AS total_duration,
    sum(activity_coefficient) AS total_activity, -- заменили avg на sum
    sum(chat_messages_cnt) AS total_messages
FROM gaming.sessions
GROUP BY hour, server_id;