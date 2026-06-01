from typing import TypedDict

class EnemyStats(TypedDict):
    hp: int
    attack: int
    speed: int

ENEMY_TYPES: dict[str, EnemyStats] = {
    "Rat":        {"hp": 4,  "attack": 1,  "speed": 1},
    "Spider":     {"hp": 6,  "attack": 2,  "speed": 1},
    "Goblin":     {"hp": 10, "attack": 3,  "speed": 1},
    "Skeleton":   {"hp": 15, "attack": 4,  "speed": 1},
    "Zombie":     {"hp": 18, "attack": 4,  "speed": 1},
    "Troll":      {"hp": 20, "attack": 5,  "speed": 1},
    "Dark Mage":  {"hp": 12, "attack": 6,  "speed": 1},
    "Orc":        {"hp": 25, "attack": 6,  "speed": 1},
    "Wraith":     {"hp": 8,  "attack": 7,  "speed": 1},
    "Vampire":    {"hp": 22, "attack": 8,  "speed": 1},
    "Dragon":     {"hp": 50, "attack": 15, "speed": 1},
}

def get_stats(name: str) -> EnemyStats:
    if name in ENEMY_TYPES:
        return ENEMY_TYPES[name]
    return {"hp": 10, "attack": 3, "speed": 1}
