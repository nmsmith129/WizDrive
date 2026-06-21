import sys

# 0 = pygame visualizer
# 1 = text visualizer (terminal, real-time keypresses)
VISUALIZER = 0

import pygame
pygame.init()

from . import map_loader
map_loader.debug = False
from .map_loader import load_map_file
from .game_state import GameState

if VISUALIZER == 0:
    from .map_visualizer import MapVisualizer
elif VISUALIZER == 1:
    from .text_visualizer import render_floor



def run_pygame(state):
    # Runs the pygame event loop, drawing the dungeon and routing WASD keypresses into game state.
    grid_size = len(state.grid)
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
                    state.apply_key("w")
                elif event.key == pygame.K_s:
                    state.apply_key("s")
                elif event.key == pygame.K_a:
                    state.apply_key("a")
                elif event.key == pygame.K_d:
                    state.apply_key("d")

        screen.fill((0, 0, 0))
        visualizer.draw(
            (state.grid, state.player.location, state.player.facing, state.enemies, state.items, state.stairs),
            state.player,
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def run_text(state):
    # Runs a terminal-mode game loop, redrawing the ASCII map after each keypress.
    import msvcrt
    print("Controls: W=forward, S=backward, A=turn left, D=turn right, Q=quit")
    render_floor(
        (state.grid, state.player.location, state.player.facing, state.enemies, state.items, state.stairs),
        state.floor_index + 1,
    )

    while True:
        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
        if key == "q":
            break
        elif key in ("w", "s", "a", "d"):
            state.apply_key(key)
            render_floor(
                (state.grid, state.player.location, state.player.facing, state.enemies, state.items, state.stairs),
                state.floor_index + 1,
            )


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        print("Usage: python -m wiz_drive.wiz_drive_main <file.dngn>")
        sys.exit(1)

    path = argv[0]
    if not path.endswith(".dngn"):
        print(f"Error: '{path}' is not a .dngn file.")
        sys.exit(1)

    _, _, floors = load_map_file(path)
    state = GameState.new(path, floors)

    if VISUALIZER == 0:
        run_pygame(state)
    elif VISUALIZER == 1:
        run_text(state)


if __name__ == "__main__":
    main()
