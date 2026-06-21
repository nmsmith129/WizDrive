import sys
import pygame
pygame.init()

from . import map_loader
map_loader.debug = False
from .map_loader import load_map_file
from .player import Player

WALL   = "#"
FLOOR  = "."
ENEMY  = "E"
ITEM   = "I"
PLAYER = "@"
STAIRS = ">"

_FACING_ARROW = {
    "north": "^ (North)",
    "south": "v (South)",
    "east":  "> (East)",
    "west":  "< (West)",
}


def render_floor(floor, floor_num: int) -> None:
    # Prints an ASCII grid of the current floor to stdout with player, enemy, item, and stair symbols.
    grid, player_pos, facing, enemies, items, stairs = floor
    grid_size = len(grid)

    enemy_positions  = {(e.grid_x, e.grid_y) for e in enemies}
    item_positions   = {(i.grid_x, i.grid_y) for i in items}
    stairs_pos       = stairs if stairs else (-1, -1)
    px, py = player_pos

    print(f"--- Floor {floor_num} ---")
    for gy in range(grid_size - 1, -1, -1):
        row = ""
        for gx in range(grid_size):
            if (gx, gy) == (px, py):
                row += PLAYER
            elif (gx, gy) in enemy_positions:
                row += ENEMY
            elif (gx, gy) in item_positions:
                row += ITEM
            elif (gx, gy) == stairs_pos:
                row += STAIRS
            elif grid[gy][gx] == 1:
                row += WALL
            else:
                row += FLOOR
        print(row)

    arrow = _FACING_ARROW.get(facing, facing)
    print(f"Player facing: {arrow}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m wiz_drive.text_visualizer <file.dngn>")
        sys.exit(1)

    path = sys.argv[1]
    if not path.endswith(".dngn"):
        print(f"Error: '{path}' is not a .dngn file.")
        sys.exit(1)

    _, _, floors = load_map_file(path)
    render_floor(floors[0], 1)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        print("Usage: python -m wiz_drive.text_visualizer <file.dngn>")
        sys.exit(1)

    path = argv[0]
    if not path.endswith(".dngn"):
        print(f"Error: '{path}' is not a .dngn file.")
        sys.exit(1)

    _, _, floors = load_map_file(path)
    render_floor(floors[0], 1)


if __name__ == "__main__":
    main()
