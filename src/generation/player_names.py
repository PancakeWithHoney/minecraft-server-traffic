# name_generator.py

import random

PREFIXES = [
    "Bot",
    "Kot",
    "Player",
    "Steve",
    "Alex",
    "Igrok",
    "Zombie",
    "Alina",
    "Grifer",
    "Professional",
    "Weird",
    "Admin",
    "Pavel",
    "Dog",
    "Bulka",
    "Buldog",
    "MC"
]

WORDS = [
    "Pelmen",
    "Cheburek",
    "Killer",
    "Noob",
    "1000LVL",
    "Sobaka",
    "Korobka",
    "Kvadrat",
    "Dancer",
    "Bot",
    "Master",
    "Gamer",
    "Game",
    "Assasin",
    "Legend",
    "Hacker",
    "Ninja",
    "Pro",
    "DANGER",
    "Hunter",
    "Creeper",
]


def generate_nickname() -> str:
    prefix = random.choice(PREFIXES)
    word = random.choice(WORDS)
    number = random.randint(1, 9999)

    return f"{prefix}_{word}{number}"
