from typing import TypedDict

import pygame


TILE_SIZE = 32 # size of each dimension of a tile in pixels


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name: str, hp: int = 1, attack: int = 1, speed: int = 1, grid_x: int = 0, grid_y: int = 0, xp: int = 0, loaded_image: pygame.Surface | None = None):
        # Initializes the enemy sprite with combat stats, grid position, and xp reward.
        super().__init__()
        self.name = name # Name of the enemy, used for identification and display purposes
        self.hp = hp # Hit points, determines how much damage the enemy can take before being defeated
        self.attack = attack # Attack power, determines how much damage the enemy can deal
        self.speed = speed  # Default speed, can be modified for different enemy types
        self.grid_x = grid_x # X position of the enemy in the grid
        self.grid_y = grid_y # Y position of the enemy in the grid
        self.xp = xp # Experience points rewarded for defeating the enemy
        if loaded_image is not None:
            self.image = pygame.transform.scale(loaded_image, (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((220, 50, 50))

    def __str__(self):
        # Returns a string summary of the enemy's name and current stats.
        return f"{self.name} (HP: {self.hp}, Attack: {self.attack}, Speed: {self.speed}, XP: {self.xp})"


class EnemyStats(TypedDict):
    hp: int
    attack: int
    speed: int
    xp: int


ENEMY_TYPES: dict[str, EnemyStats] = {
    "Rat":        {"hp": 4,  "attack": 1,  "speed": 1, "xp": 5},
    "Spider":     {"hp": 6,  "attack": 2,  "speed": 1, "xp": 10},
    "Goblin":     {"hp": 10, "attack": 3,  "speed": 1, "xp": 15},
    "Skeleton":   {"hp": 15, "attack": 4,  "speed": 1, "xp": 20},
    "Zombie":     {"hp": 18, "attack": 4,  "speed": 1, "xp": 25},
    "Troll":      {"hp": 20, "attack": 5,  "speed": 1, "xp": 30},
    "Dark Mage":  {"hp": 12, "attack": 6,  "speed": 1, "xp": 35},
    "Orc":        {"hp": 25, "attack": 6,  "speed": 1, "xp": 40},
    "Wraith":     {"hp": 8,  "attack": 7,  "speed": 1, "xp": 45},
    "Vampire":    {"hp": 22, "attack": 8,  "speed": 1, "xp": 50},
    "Dragon":     {"hp": 50, "attack": 15, "speed": 1, "xp": 100},
}


def get_stats(name: str) -> EnemyStats:
    # Returns the stat block for a named enemy type, falling back to defaults for unknown names.
    if name in ENEMY_TYPES:
        return ENEMY_TYPES[name]
    return {"hp": 10, "attack": 3, "speed": 1, "xp": 0}