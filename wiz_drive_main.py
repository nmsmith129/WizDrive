import sys

# 0 = pygame visualizer
# 1 = text visualizer (terminal, real-time keypresses)
# 2 = ClaudeCode visualizer (single keystroke arg, saves state between runs)
VISUALIZER = 2

import pygame
pygame.init()

import map_loader
map_loader.debug = False
from map_loader import load_map_file
from game_state import GameState

if VISUALIZER == 0:
    from map_visualizer import map_visualizer
elif VISUALIZER == 1:
    from text_visualizer import render_floor
elif VISUALIZER == 2:
    import claude_code_visualizer


def run_pygame(state):
    # Runs the pygame event loop, drawing the dungeon and routing WASD keypresses into game state.
    grid_size = len(state.grid)
    tile_size = 32
    screen = pygame.display.set_mode((grid_size * tile_size, grid_size * tile_size))
    pygame.display.set_caption("WizDrive")
    visualizer = map_visualizer(screen, tile_size=tile_size)
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
            (state.grid, state.player.location, state.player.facing, state.enemies, state.items),
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


if __name__ == "__main__":
    if VISUALIZER == 2:
        claude_code_visualizer.run(
            dungeon_path=sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".dngn") else None,
            key=sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith(".dngn") else None,
        )
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python wiz_drive_main.py <file.dngn>")
        sys.exit(1)

    path = sys.argv[1]
    if not path.endswith(".dngn"):
        print(f"Error: '{path}' is not a .dngn file.")
        sys.exit(1)

    _, _, floors = load_map_file(path)
    state = GameState.new(path, floors)

    if VISUALIZER == 0:
        run_pygame(state)
    elif VISUALIZER == 1:
        run_text(state)
