import pygame


TILE_SIZE = 32


class Item(pygame.sprite.Sprite):
    def __init__(self, name: str, value: int, description: str):
        super().__init__()
        self.name = name
        self.value = value
        self.description = description
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((220, 190, 50))
        self.rect = self.image.get_rect()

    def __str__(self):
        return f"{self.name} (Value: {self.value}) - {self.description}"