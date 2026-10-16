# name_generator.py

import random

PREFIXES = [
    "Ka",
    "Ba",
    "Nu",
    "Ku",
    "Ru",
    "Ta",
    "La",
    "Lo",
    "Re",
    "Hru",
    "Aba",
    "Abo",
    "De"
]

POSTFIXES = [
    "bik",
    "sik",
    "rasik",
    "zast"
    "mzik",
    "psik",
    "st",
    "duk",
    "tuk",
    "sov",
    "bovich"
]

WORDS = [
    "Master",
    "Gamer",
    "Game",
    "Assasin",
    "Legend",
    "Hacker",
    "Ninja",
    "Pro",
    "Hunter",
    "Creeper",
    "404"
]


def generate_nickname() -> str:
    prefix = random.choice(PREFIXES)
    postfix = random.choice(POSTFIXES)
    word = random.choice(WORDS)
    number = random.randint(1, 9999)

    return f"{prefix}{postfix}_{word}{number}"

for i in range(100):
    print(generate_nickname())