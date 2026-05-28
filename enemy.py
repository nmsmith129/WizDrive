import pygame


TILE_SIZE = 32


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name: str, hp: int = 1, attack: int = 1, speed: int = 1, grid_x: int = 0, grid_y: int = 0):
        super().__init__()
        self.name = name # Name of the enemy, used for identification and display purposes
        self.hp = hp # Hit points, determines how much damage the enemy can take before being defeated
        self.attack = attack #``
        self.speed = speed  # Default speed, can be modified for different enemy types
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((220, 50, 50))
        self.rect = self.image.get_rect(topleft=(grid_x * TILE_SIZE, grid_y * TILE_SIZE))

    def __str__(self):
        return f"{self.name} (HP: {self.hp}, Attack: {self.attack}, Speed: {self.speed})"