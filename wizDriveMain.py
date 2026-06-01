import sys

# 0 = pygame visualizer
# 1 = text visualizer (terminal, real-time keypresses)
# 2 = ClaudeCode visualizer (single keystroke arg, saves state between runs)
VISUALIZER = 2

import pygame
pygame.init()

import mapLoader
mapLoader.debug = False
from mapLoader import loadMapFile
from player import Player

if VISUALIZER == 0:
    from mapVisualizer import MapVisualizer
elif VISUALIZER == 1:
    from textVisualizer import render_floor
elif VISUALIZER == 2:
    import ClaudeCodeVisualizer


def _is_wall(grid, x, y):
    grid_size = len(grid)
    if x < 0 or y < 0 or x >= grid_size or y >= grid_size:
        return True
    return grid[y][x] == 1


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


def run_pygame(floor, player):
    grid = floor[0]
    grid_size = len(grid)
    tile_size = 32
    screen = pygame.display.set_mode((grid_size * tile_size, grid_size * tile_size))
    pygame.display.set_caption("WizDrive")
    visualizer = MapVisualizer(screen, tile_size=tile_size)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_w:
                    nx, ny = _next_pos(player)
                    if not _is_wall(grid, nx, ny):
                        player.move("forward")
                elif event.key == pygame.K_s:
                    bx, by = _behind_pos(player)
                    if not _is_wall(grid, bx, by):
                        player.move("backward")
                elif event.key == pygame.K_a:
                    player.turn("left")
                elif event.key == pygame.K_d:
                    player.turn("right")

        screen.fill((0, 0, 0))
        visualizer.draw(floor, player)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def run_text(floor, player):
    import msvcrt
    grid = floor[0]
    print("Controls: W=forward, S=backward, A=turn left, D=turn right, Q=quit")
    render_floor((grid, player.location, player.facing, floor[3], floor[4]), 1)

    while True:
        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
        if key == "q":
            break
        elif key == "w":
            nx, ny = _next_pos(player)
            if not _is_wall(grid, nx, ny):
                player.move("forward")
            else:
                print("Blocked by a wall.")
                continue
        elif key == "s":
            bx, by = _behind_pos(player)
            if not _is_wall(grid, bx, by):
                player.move("backward")
            else:
                print("Blocked by a wall.")
                continue
        elif key == "a":
            player.turn("left")
        elif key == "d":
            player.turn("right")
        else:
            continue

        render_floor((grid, player.location, player.facing, floor[3], floor[4]), 1)


if __name__ == "__main__":
    if VISUALIZER == 2:
        # ClaudeCode visualizer handles its own args (dungeon file or keystroke)
        ClaudeCodeVisualizer.run(
            dungeon_path=sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".dngn") else None,
            key=sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith(".dngn") else None,
        )
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python wizDriveMain.py <file.dngn>")
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

    if VISUALIZER == 0:
        run_pygame(floor, player)
    elif VISUALIZER == 1:
        run_text(floor, player)
