import sys
import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "game_state.json")

PLAYER_ATTACK = 5

import pygame
pygame.init()

import mapLoader
mapLoader.debug = False
from mapLoader import loadMapFile
from player import Player
from enemy import Enemy
from textVisualizer import render_floor


def _is_wall(grid, x, y):
    size = len(grid)
    if x < 0 or y < 0 or x >= size or y >= size:
        return True
    return grid[y][x] == 1


def _enemy_at(enemies, x, y):
    for e in enemies:
        if e.grid_x == x and e.grid_y == y:
            return e
    return None


def _next_pos(player):
    x, y = player.location
    deltas = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
    dx, dy = deltas[player.facing]
    return x + dx, y + dy


def _behind_pos(player):
    x, y = player.location
    deltas = {"north": (0, -1), "south": (0, 1), "east": (-1, 0), "west": (1, 0)}
    dx, dy = deltas[player.facing]
    return x + dx, y + dy


def _do_combat(player, enemy, enemies):
    enemy.hp -= PLAYER_ATTACK
    print(f"You attack {enemy.name} for {PLAYER_ATTACK} damage! ({enemy.hp} HP remaining)")
    if enemy.hp <= 0:
        print(f"{enemy.name} is defeated!")
        enemies.remove(enemy)
    else:
        player.hp -= enemy.attack
        print(f"{enemy.name} hits back for {enemy.attack} damage! (Your HP: {player.hp})")
        if player.hp <= 0:
            print("You have been defeated!")


def save_state(dungeon_path, floor_index, player, enemies):
    state = {
        "dungeon": dungeon_path,
        "floor": floor_index,
        "x": player.location[0],
        "y": player.location[1],
        "facing": player.facing,
        "hp": player.hp,
        "mp": player.mp,
        "enemies": [
            {"name": e.name, "hp": e.hp, "attack": e.attack, "speed": e.speed,
             "grid_x": e.grid_x, "grid_y": e.grid_y}
            for e in enemies
        ],
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def _enemies_from_state(data):
    return [
        Enemy(e["name"], hp=e["hp"], attack=e["attack"], speed=e["speed"],
              grid_x=e["grid_x"], grid_y=e["grid_y"])
        for e in data
    ]


def run(dungeon_path=None, key=None):
    _, _, floors = loadMapFile(dungeon_path) if dungeon_path else (None, None, None)

    if dungeon_path:
        floor_index = 0
        floor = floors[0]
        grid, start_pos, start_facing, enemies, items, stairs = floor
        player = Player("Hero", hp=20, mp=10)
        player.location = start_pos
        player.facing = start_facing
        save_state(dungeon_path, floor_index, player, enemies)
    else:
        state = load_state()
        dungeon_path = state["dungeon"]
        _, _, floors = loadMapFile(dungeon_path)
        floor_index = state["floor"]
        floor = floors[floor_index]
        grid, _, _, _, items, stairs = floor
        enemies = _enemies_from_state(state["enemies"])
        player = Player("Hero", hp=state["hp"], mp=state["mp"])
        player.location = (state["x"], state["y"])
        player.facing = state["facing"]

    if key:
        key = key.lower()
        if key in ("w", "s"):
            nx, ny = _next_pos(player) if key == "w" else _behind_pos(player)
            target = _enemy_at(enemies, nx, ny)
            if target:
                _do_combat(player, target, enemies)
            elif _is_wall(grid, nx, ny):
                print("Blocked by a wall.")
            else:
                player.move("forward" if key == "w" else "backward")
                # Check for stairs after moving
                if stairs and player.location == stairs:
                    next_index = floor_index + 1
                    if next_index < len(floors):
                        print(f"You descend to floor {next_index + 1}.")
                        floor_index = next_index
                        floor = floors[floor_index]
                        grid, start_pos, start_facing, enemies, items, stairs = floor
                        player.location = start_pos
                        player.facing = start_facing
                    else:
                        print("These stairs lead nowhere... yet.")
        elif key == "a":
            player.turn("left")
        elif key == "d":
            player.turn("right")

    save_state(dungeon_path, floor_index, player, enemies)
    render_floor((grid, player.location, player.facing, enemies, items, stairs), floor_index + 1)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg and arg.endswith(".dngn"):
        run(dungeon_path=arg)
    elif arg:
        if not os.path.exists(STATE_FILE):
            print("No saved state. Run with a .dngn file first: python ClaudeCodeVisualizer.py <file.dngn>")
            sys.exit(1)
        run(key=arg)
    else:
        if not os.path.exists(STATE_FILE):
            print("No saved state. Run with a .dngn file first: python ClaudeCodeVisualizer.py <file.dngn>")
            sys.exit(1)
        run()
