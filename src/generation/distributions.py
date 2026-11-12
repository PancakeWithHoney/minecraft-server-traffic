import math
import random


def poisson(lam: float, rng: random.Random) -> int:
    if lam <= 0:
        return 0

    limit = math.exp(-lam)
    count = 0
    product = 1.0

    while product > limit:
        count += 1
        product *= rng.random()

    return count - 1