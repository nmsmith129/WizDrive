import sys

# 0 = pygame visualizer (top-down)
# 1 = text visualizer (terminal, real-time keypresses)
# 2 = first-person (pygame raycaster)
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
elif VISUALIZER == 2:
    from .first_person import FirstPersonVisualizer



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


def run_first_person(state):
    # Runs the pygame event loop in first-person, routing WASD through the shared game
    # state so collision, combat, and stair transitions behave exactly as in top-down mode.
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("WizDrive — First Person")
    visualizer = FirstPersonVisualizer(screen)
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

        visualizer.draw(state.grid, state.player)
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
    elif VISUALIZER == 2:
        run_first_person(state)


if __name__ == "__main__":
    main()
