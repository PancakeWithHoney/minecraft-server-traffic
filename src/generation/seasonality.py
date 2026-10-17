from __future__ import annotations

import math
from datetime import datetime


def diurnal_factor(at: datetime) -> float:
    """Суточный цикл активности игроков.

    Пик — около 20:00, минимум — около 08:00.
    Возвращает значение от -1 до 1.
    """
    hour = at.hour + at.minute / 60.0 + at.second / 3600.0
    # cos(2π * (hour - 20) / 24): 1 в 20:00, -1 в 08:00.
    return math.cos(2.0 * math.pi * (hour - 20.0) / 24.0)


def annual_factor(at: datetime) -> float:
    """Годовой цикл активности игроков.

    Пик — примерно в середине июля,
    минимум — примерно в середине января.
    Возвращает значение от -1 до 1.
    """
    day_of_year = float(at.timetuple().tm_yday)
    return math.cos(2.0 * math.pi * (day_of_year - 196.0) / 365.25)