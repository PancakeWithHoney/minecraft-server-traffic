# name_generator.py
from __future__ import annotations
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

def generate_nickname(rng: random.Random) -> str:
    prefix = rng.choice(PREFIXES)
    word = rng.choice(WORDS)
    number = rng.randint(1, 9999)
    return f"{prefix}_{word}{number}"
