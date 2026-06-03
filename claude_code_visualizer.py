import sys
import os

import pygame
pygame.init()

import map_loader
map_loader.debug = False
from map_loader import load_map_file
from game_state import GameState, STATE_FILE
from text_visualizer import render_floor


def run(dungeon_path=None, key=None):
    # Loads or resumes a dungeon run, applies an optional keypress, then renders the current floor.
    if dungeon_path:
        _, _, floors = load_map_file(dungeon_path)
        state = GameState.new(dungeon_path, floors)
        state.save()
    else:
        state = GameState.from_save()

    if key:
        state.apply_key(key)
        state.save()

    render_floor(
        (state.grid, state.player.location, state.player.facing, state.enemies, state.items, state.stairs),
        state.floor_index + 1,
    )


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg and arg.endswith(".dngn"):
        run(dungeon_path=arg)
    elif arg:
        if not os.path.exists(STATE_FILE):
            print("No saved state. Run with a .dngn file first: python claude_code_visualizer.py <file.dngn>")
            sys.exit(1)
        run(key=arg)
    else:
        if not os.path.exists(STATE_FILE):
            print("No saved state. Run with a .dngn file first: python claude_code_visualizer.py <file.dngn>")
            sys.exit(1)
        run()
