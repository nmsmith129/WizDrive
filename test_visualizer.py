import sys
import pygame

# pygame must be initialized before loadMapFile, since Enemy/Item create
# pygame.Surface objects in their constructors during map parsing.
pygame.init()

from mapLoader import loadMapFile
from mapVisualizer import run_debug_viewer
from player import Player

if len(sys.argv) < 2:
    print("Error: no dungeon file specified. Usage: python test_visualizer.py <file.dngn>")
    sys.exit(1)

path = sys.argv[1]
if not path.endswith(".dngn"):
    print(f"Error: '{path}' is not a .dngn file.")
    sys.exit(1)

_, _, floors = loadMapFile(path)

floor = floors[0]
grid, start_pos, start_facing, enemies, items = floor

player = Player("Hero", hp=20, mp=10)
player.location = start_pos
player.facing = start_facing

print(f"Floor 1: {len(grid)}x{len(grid)} grid")
print(f"Player start: {player.location}, facing {player.facing}")
print(f"Enemies: {[e.name for e in enemies]}")
print(f"Items:   {[i.name for i in items]}")

run_debug_viewer(floor, player)
