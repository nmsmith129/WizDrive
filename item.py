from typing import NotRequired, TypedDict

import pygame


TILE_SIZE = 32


class Item(pygame.sprite.Sprite):
    def __init__(self, name: str, value: int, description: str, grid_x: int = 0, grid_y: int = 0,
                 category: str = "misc", effect: dict[str, int] | None = None):
        # Initializes the item sprite with name, value, description, category, effect, and grid position.
        super().__init__()
        self.name = name
        self.value = value
        self.description = description
        self.category = category  # "weapon" | "armor" | "consumable" | "treasure" | "misc"
        self.effect = effect or {}  # category-specific bonuses, e.g. {"strength": 4} or {"heal": 15}
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((220, 190, 50))
        self.rect = self.image.get_rect(topleft=(grid_x * TILE_SIZE, grid_y * TILE_SIZE))

    @property
    def strength(self) -> int:
        # Returns the weapon attack bonus stored in effect, or 0 for non-weapon items.
        return self.effect.get("strength", 0)

    def __str__(self):
        # Returns a string summary of the item's name, category, value, and description.
        return f"{self.name} [{self.category}] (Value: {self.value}) - {self.description}"


class ItemStats(TypedDict):
    value: int
    category: str
    description: str
    strength: NotRequired[int]  # weapons: attack bonus added to the wielder's strength
    heal: NotRequired[int]  # consumables: HP restored on use


ITEM_TYPES: dict[str, ItemStats] = {
    "Gold Coin":     {"value": 5,   "category": "treasure",   "description": "A shiny gold coin"},
    "Ancient Scroll":{"value": 50,  "category": "treasure",   "description": "Inscribed with an unknown spell"},
    "Iron Key":      {"value": 5,   "category": "misc",       "description": "Opens a locked door somewhere"},
    "Health Potion": {"value": 20,  "category": "consumable", "heal": 15,    "description": "Restores 15 HP"},
    "Mana Potion":   {"value": 20,  "category": "consumable", "heal": 0,     "description": "Restores spent mana"},
    "Dagger":        {"value": 15,  "category": "weapon",     "strength": 2, "description": "A small, quick blade"},
    "Iron Sword":    {"value": 30,  "category": "weapon",     "strength": 4, "description": "A sturdy iron blade"},
    "Battle Axe":    {"value": 55,  "category": "weapon",     "strength": 7, "description": "A heavy two-handed axe"},
    "Leather Armor": {"value": 25,  "category": "armor",      "description": "Light protective hide"},
}


def get_item_stats(name: str) -> ItemStats:
    # Returns the stat block for a named item type, falling back to a generic misc item for unknown names.
    if name in ITEM_TYPES:
        return ITEM_TYPES[name]
    return {"value": 1, "category": "misc", "description": ""}
