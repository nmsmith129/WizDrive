import json
import os

import map_loader
map_loader.debug = False
from map_loader import load_map_file
from player import Player
from enemy import Enemy
from item import Item

STATE_FILE = os.path.join(os.path.dirname(__file__), "game_state.json")
SCHEMA_VERSION: int = 2


class GameState:
    def __init__(self, dungeon_path, floors, floor_index, player, enemies):
        # Stores all runtime game state: dungeon path, loaded floors, current floor index, player, and enemy list.
        self.dungeon_path = dungeon_path
        self.floors = floors
        self.floor_index = floor_index
        self.player = player
        self.enemies = enemies

    @property
    def grid(self):
        # Returns the tile grid for the current floor.
        return self.floors[self.floor_index][0]

    @property
    def items(self):
        # Returns the item list for the current floor.
        return self.floors[self.floor_index][4]

    @property
    def stairs(self):
        # Returns the stair coordinates for the current floor, or None if absent.
        return self.floors[self.floor_index][5]

    @classmethod
    def new(cls, dungeon_path, floors):
        # Creates a fresh GameState from the first floor of a loaded dungeon, with a default Hero player.
        grid, start_pos, start_facing, enemies, items, stairs = floors[0]
        player = Player("Hero")
        player.location = start_pos
        player.facing = start_facing
        return cls(dungeon_path, floors, 0, player, list(enemies))

    @classmethod
    def from_save(cls):
        # Reconstructs a GameState by loading the JSON save file and re-parsing its dungeon.
        with open(STATE_FILE) as f:
            data = json.load(f)
        save_version = data.get("schema_version", 0)
        if save_version > SCHEMA_VERSION:
            raise ValueError(
                f"Save is from a newer version of WizDrive "
                f"(save {save_version!r} > supported {SCHEMA_VERSION!r})."
            )
        _, _, floors = load_map_file(data["dungeon"])
        player = Player("Hero", hp=data["hp"], mp=data["mp"])
        player.location = (data["x"], data["y"])
        player.facing = data["facing"]
        player.attack = data.get("attack", 0.5)
        player.strength = data.get("strength", 1)
        player.defense = data.get("defense", 1)
        player.max_hp = data.get("max_hp", 10)
        player.intelligence = data.get("intelligence", 1)
        player.mana = data.get("mana", 1)
        player.xp = data.get("xp", 0)
        player.level = data.get("level", 1)
        enemies = [
            Enemy(e["name"], hp=e["hp"], attack=e["attack"], speed=e["speed"],
                  grid_x=e["grid_x"], grid_y=e["grid_y"], xp=e.get("xp", 0))
            for e in data["enemies"]
        ]
        inv_entries = data.get("inventory", [])
        inventory: list[Item] = []
        for entry in inv_entries:
            item = Item(
                entry["name"], entry["value"], entry["description"],
                entry["grid_x"], entry["grid_y"],
                category=entry["category"], effect=entry["effect"],
            )
            item.origin_floor = entry.get("origin_floor")
            inventory.append(item)
        player.inventory = inventory
        eq = data.get("equipped_weapon")
        if eq is not None:
            player.weapon = player.inventory[eq]
        for inv_item in player.inventory:
            origin = inv_item.origin_floor
            if origin is not None and origin < len(floors):
                floor_items = floors[origin][4]
                for floor_item in list(floor_items):
                    if (floor_item.grid_x == inv_item.grid_x
                            and floor_item.grid_y == inv_item.grid_y
                            and floor_item.name == inv_item.name):
                        floor_items.remove(floor_item)
                        break
        return cls(data["dungeon"], floors, data["floor"], player, enemies)

    def save(self):
        # Serializes the current game state to the JSON save file.
        data = {
            "schema_version": SCHEMA_VERSION,
            "dungeon": self.dungeon_path,
            "floor": self.floor_index,
            "x": self.player.location[0],
            "y": self.player.location[1],
            "facing": self.player.facing,
            "hp": self.player.hp,
            "mp": self.player.mp,
            "attack": self.player.attack,
            "strength": self.player.strength,
            "defense": self.player.defense,
            "max_hp": self.player.max_hp,
            "intelligence": self.player.intelligence,
            "mana": self.player.mana,
            "xp": self.player.xp,
            "level": self.player.level,
            "enemies": [
                {"name": e.name, "hp": e.hp, "attack": e.attack, "speed": e.speed,
                 "grid_x": e.grid_x, "grid_y": e.grid_y, "xp": e.xp}
                for e in self.enemies
            ],
            "inventory": [
                {
                    "name": item.name,
                    "value": item.value,
                    "description": item.description,
                    "category": item.category,
                    "effect": item.effect,
                    "grid_x": item.grid_x,
                    "grid_y": item.grid_y,
                    "origin_floor": getattr(item, "origin_floor", None),
                }
                for item in self.player.inventory
            ],
            "equipped_weapon": next(
                (i for i, inv_item in enumerate(self.player.inventory)
                 if inv_item is self.player.weapon),
                None,
            ),
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)

    def _is_wall(self, x, y):
        # Returns True if (x, y) is out of bounds or a wall tile.
        grid = self.grid
        size = len(grid)
        return x < 0 or y < 0 or x >= size or y >= size or grid[y][x] == 1

    def _enemy_at(self, x, y):
        # Returns the enemy occupying grid position (x, y), or None if the tile is empty.
        for e in self.enemies:
            if e.grid_x == x and e.grid_y == y:
                return e
        return None

    def _item_at(self, x, y):
        # Returns the first item at grid position (x, y) from the current floor's item list, or None.
        for item in self.items:
            if item.grid_x == x and item.grid_y == y:
                return item
        return None

    def apply_key(self, key):
        # Processes a single keypress (WASD) and updates movement, combat, or floor transitions accordingly.
        key = key.lower()
        if key in ("w", "s"):
            nx, ny = self.player.next_pos() if key == "w" else self.player.prev_pos()
            target = self._enemy_at(nx, ny)
            if target:
                if self.player.strike(target):
                    self.enemies.remove(target)
            elif self._is_wall(nx, ny):
                print("Blocked by a wall.")
            else:
                self.player.move("forward" if key == "w" else "backward")
                while True:
                    item = self._item_at(*self.player.location)
                    if item is None:
                        break
                    item.origin_floor = self.floor_index
                    self.player.pick_up(item)
                    self.items.remove(item)
                stairs = self.stairs
                if stairs and self.player.location == stairs:
                    next_index = self.floor_index + 1
                    if next_index < len(self.floors):
                        print(f"You descend to floor {next_index + 1}.")
                        self.floor_index = next_index
                        _, start_pos, start_facing, enemies, _, _ = self.floors[self.floor_index]
                        self.player.location = start_pos
                        self.player.facing = start_facing
                        self.enemies = list(enemies)
                    else:
                        print("These stairs lead nowhere... yet.")
        elif key == "a":
            self.player.turn("left")
        elif key == "d":
            self.player.turn("right")
