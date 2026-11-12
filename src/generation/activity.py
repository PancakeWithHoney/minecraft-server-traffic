class SessionReadingGenerator:
    """Генерирует одну завершённую сессию для сервера в момент at."""

    def __init__(
        self,
        server: Server,
        gamemode_profile: GamemodeProfile,      # из catalog.profile_for(server)
        session_profile: SessionProfile,         # глобальные границы
        server_profile: ServerProfile,           # для JoinTimeSampler
        anomaly_policy: AnomalyPolicy,
        rng: random.Random,
        players: PlayerCatalog,
    ) -> None:
        self._server = server
        self._gamemode_profile = gamemode_profile
        self._rng = rng
        self._anomaly_policy = anomaly_policy
        self._players = players

        # сэмплеры — ОДИН раз в __init__ (как в weather)
        self._wait: MetricSampler = JoinTimeSampler(server_profile)
        self._duration: MetricSampler = SessionDurationSampler(session_profile)
        self._exit_picker = _ExitReasonPicker()

    @property
    def server(self) -> Server:
        return self._server

    def generate(self, at: datetime) -> PlayerSession:
        # 1) аномалия на эту сессию
        anomaly = self._anomaly_policy.decide()
        rng = self._rng

        # 2) выбираем игрока из каталога
        player = self._pick_player()

        # 3) wait_time — до сессии
        ctx = ReadingContext(at=at, gamemode=self._gamemode_profile)
        wait_ms = self._wait.sample(ctx, rng)

        # 4) JOIN_ABANDONED — если ждал дольше таймаута
        if wait_ms > self._gamemode_profile.join_timeout_ms:
            return PlayerSession(
                id=...,                       # см. §5
                join_ts=at,
                player_id=player.id,
                server_id=self._server.id,
                wait_time_ms=self._gamemode_profile.join_timeout_ms,
                duration_s=0.0,
                exit_reason=ExitReason.TIMEOUT,
                join_abandoned=True,
                is_anomaly=False,
            )

        # 5) duration — сэмплер + аномалия
        duration = self._duration.sample(ctx, rng)
        duration = self._apply_duration_anomaly(duration, anomaly)

        # 6) exit_reason — пикер (по duration + аномалии)
        exit_reason = self._exit_picker.pick(
            ctx, duration=duration, anomaly=anomaly, rng=rng
        )

        return PlayerSession(
            id=...,
            join_ts=at,
            player_id=player.id,
            server_id=self._server.id,
            wait_time_ms=wait_ms,
            duration_s=duration,
            exit_reason=exit_reason,
            join_abandoned=False,
            is_anomaly=anomaly is not None,
        )

    # --- внутренние хелперы ---

    def _pick_player(self) -> Player:
        # TODO: взвешенный выбор по role (VIP чаще, чем DEFAULT)
        idx = self._rng.randrange(len(self._players.players()))
        return self._players.by_id(idx)

    def _apply_duration_anomaly(
        self, value: float, anomaly: AnomalyKind | None
    ) -> float:
        strength = self._anomaly_policy.strength
        if anomaly == AnomalyKind.LONG_SESSIONS:
            return round(value * strength * self._rng.uniform(1.5, 2.5), 1)
        if anomaly == AnomalyKind.SHORT_SESSIONS:
            return round(max(10.0, value / strength / self._rng.uniform(1.5, 2.5)), 1)
        return value

    class BatchGenerator:
        """Пачка сессий по всем серверам на один момент времени."""

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

        def generate_batch(self, at: datetime, size: int) -> list[PlayerSession]:
            if not self._per_server:
                return []
            sessions: list[PlayerSession] = []
            for index in range(size):
                generator = self._per_server[index % len(self._per_server)]
                sessions.append(generator.generate(at))
            return sessions

class BatchGenerator:
    """Пачка сессий по всем серверам на один момент времени."""

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

    def generate_batch(self, at: datetime, size: int) -> list[PlayerSession]:
        if not self._per_server:
            return []
        sessions: list[PlayerSession] = []
        for index in range(size):
            generator = self._per_server[index % len(self._per_server)]
            sessions.append(generator.generate(at))
        return sessions