import pygame


TILE_SIZE = 32


class Item(pygame.sprite.Sprite):
    def __init__(self, name: str, value: int, description: str, grid_x: int = 0, grid_y: int = 0):
        # Initializes the item sprite with name, value, description, and grid position.
        super().__init__()
        self.name = name
        self.value = value
        self.description = description
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((220, 190, 50))
        self.rect = self.image.get_rect(topleft=(grid_x * TILE_SIZE, grid_y * TILE_SIZE))

    def __str__(self):
        # Returns a string summary of the item's name, value, and description.
        return f"{self.name} (Value: {self.value}) - {self.description}"