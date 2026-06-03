import json
import os

import map_loader
map_loader.debug = False
from map_loader import load_map_file
from player import Player
from enemy import Enemy

STATE_FILE = os.path.join(os.path.dirname(__file__), "game_state.json")


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
        player = Player("Hero", hp=50, mp=10)
        player.location = start_pos
        player.facing = start_facing
        return cls(dungeon_path, floors, 0, player, list(enemies))

    @classmethod
    def from_save(cls):
        # Reconstructs a GameState by loading the JSON save file and re-parsing its dungeon.
        with open(STATE_FILE) as f:
            data = json.load(f)
        _, _, floors = load_map_file(data["dungeon"])
        player = Player("Hero", hp=data["hp"], mp=data["mp"])
        player.location = (data["x"], data["y"])
        player.facing = data["facing"]
        player.xp = data.get("xp", 0)
        player.level = data.get("level", 1)
        enemies = [
            Enemy(e["name"], hp=e["hp"], attack=e["attack"], speed=e["speed"],
                  grid_x=e["grid_x"], grid_y=e["grid_y"], xp=e.get("xp", 0))
            for e in data["enemies"]
        ]
        return cls(data["dungeon"], floors, data["floor"], player, enemies)

    def save(self):
        # Serializes the current game state to the JSON save file.
        data = {
            "dungeon": self.dungeon_path,
            "floor": self.floor_index,
            "x": self.player.location[0],
            "y": self.player.location[1],
            "facing": self.player.facing,
            "hp": self.player.hp,
            "mp": self.player.mp,
            "xp": self.player.xp,
            "level": self.player.level,
            "enemies": [
                {"name": e.name, "hp": e.hp, "attack": e.attack, "speed": e.speed,
                 "grid_x": e.grid_x, "grid_y": e.grid_y, "xp": e.xp}
                for e in self.enemies
            ],
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

    def apply_key(self, key):
        # Processes a single keypress (WASD) and updates movement, combat, or floor transitions accordingly.
        key = key.lower()
        if key in ("w", "s"):
            nx, ny = self.player.next_pos() if key == "w" else self.player.prev_pos()
            target = self._enemy_at(nx, ny)
            if target:
                if self.player.attack(target):
                    self.enemies.remove(target)
            elif self._is_wall(nx, ny):
                print("Blocked by a wall.")
            else:
                self.player.move("forward" if key == "w" else "backward")
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
