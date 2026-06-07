from __future__ import annotations

import pygame

from mapLoader import FloorData
from player import Player

WALL_COLOR   = (60,  60,  60)
FLOOR_COLOR  = (200, 200, 200)
ENEMY_COLOR  = (220, 50,  50)
ITEM_COLOR   = (220, 190, 50)
PLAYER_COLOR = (50,  200, 50)
FACING_COLOR = (255, 255, 255)

_FACING_DELTA: dict[str, tuple[int, int]] = {
    "north": (0, -1),
    "east":  (1,  0),
    "south": (0,  1),
    "west":  (-1, 0),
}


class MapVisualizer:
    def __init__(
        self,
        surface: pygame.Surface,
        tile_size: int = 32,
        offset: tuple[int, int] = (0, 0),
    ) -> None:
        self.surface = surface
        self.tile_size = tile_size
        self.offset = offset

    def _to_screen(self, grid_x: int, grid_y: int, grid_size: int) -> tuple[int, int]:
        """Return the top-left screen pixel for a tile at (grid_x, grid_y)."""
        ox, oy = self.offset
        return (
            grid_x * self.tile_size + ox,
            (grid_size - 1 - grid_y) * self.tile_size + oy,
        )

    def draw(self, floor_data: FloorData, player: Player | None = None) -> None:
        grid, player_pos, facing, enemies, items = floor_data
        grid_size = len(grid)
        ts = self.tile_size

        # 1. Tiles
        for gy in range(grid_size):
            for gx in range(grid_size):
                color = WALL_COLOR if grid[gy][gx] == 1 else FLOOR_COLOR
                sx, sy = self._to_screen(gx, gy, grid_size)
                pygame.draw.rect(self.surface, color, (sx, sy, ts, ts))

        # 2. Items (1px inset so the tile border shows through)
        for item in items:
            sx, sy = self._to_screen(item.grid_x, item.grid_y, grid_size)
            pygame.draw.rect(self.surface, ITEM_COLOR, (sx + 1, sy + 1, ts - 2, ts - 2))

        # 3. Enemies
        for enemy in enemies:
            sx, sy = self._to_screen(enemy.grid_x, enemy.grid_y, grid_size)
            pygame.draw.rect(self.surface, ENEMY_COLOR, (sx + 1, sy + 1, ts - 2, ts - 2))

        # 4. Player — use live Player object if provided, otherwise fall back to map start data
        if player is not None:
            px, py = player.location
            facing_dir = player.facing
        else:
            px, py = player_pos
            facing_dir = facing

        sx, sy = self._to_screen(px, py, grid_size)
        pygame.draw.rect(self.surface, PLAYER_COLOR, (sx + 1, sy + 1, ts - 2, ts - 2))

        # Facing indicator — white line from tile centre toward the faced edge
        cx, cy = sx + ts // 2, sy + ts // 2
        dx, dy = _FACING_DELTA.get(facing_dir, (0, 0))
        pygame.draw.line(
            self.surface,
            FACING_COLOR,
            (cx, cy),
            (cx + dx * ts // 2, cy + dy * ts // 2),
            2,
        )


def run_debug_viewer(floor_data: FloorData, player: Player | None = None) -> None:
    """Open a standalone pygame window showing the floor. Close with the window button or Q."""
    pygame.init()
    grid_size = len(floor_data[0])
    tile_size = 32
    screen = pygame.display.set_mode((grid_size * tile_size, grid_size * tile_size))
    pygame.display.set_caption("WizDrive — Debug Map Viewer")

    visualizer = MapVisualizer(screen, tile_size=tile_size)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        screen.fill((0, 0, 0))
        visualizer.draw(floor_data, player)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
