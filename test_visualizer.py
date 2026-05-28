import pygame

# pygame must be initialized before loadMapFile, since Enemy/Item create
# pygame.Surface objects in their constructors during map parsing.
pygame.init()

from mapLoader import loadMapFile
from mapVisualizer import run_debug_viewer
from player import Player

_, _, floors = loadMapFile("DebugMapLoader.dngn")

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
