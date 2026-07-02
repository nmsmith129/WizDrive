from __future__ import annotations

import pygame

from .player import Player

# Direction vectors match player._FORWARD_DELTAS exactly (north = +y). Because the
# grid is already y-up, the raycast needs no coordinate flipping.
_DIR_VEC: dict[str, tuple[float, float]] = {
    "north": (0.0, 1.0), "east": (1.0, 0.0),
    "south": (0.0, -1.0), "west": (-1.0, 0.0),
}

FOV = 0.66               # camera-plane half-length; ~66-degree field of view
WALL_NS = (90, 90, 90)   # walls hit on a north/south face
WALL_EW = (60, 60, 60)   # east/west faces drawn darker for cheap fake shading
CEILING = (25, 25, 35)
FLOOR   = (40, 35, 30)

_FAR = 1e30              # sentinel "no wall hit" distance


def _cast_column(grid, px: float, py: float, ray_dx: float, ray_dy: float) -> tuple[float, int]:
    # Marches a single ray from (px, py) using DDA until it hits a wall (1) or leaves
    # the grid. Returns (perpendicular distance, side) where side 0 = vertical (x) wall
    # face and side 1 = horizontal (y) wall face. Perpendicular distance avoids fisheye.
    map_x, map_y = int(px), int(py)
    # Distance the ray travels to cross one full grid cell in x / in y.
    delta_x = abs(1.0 / ray_dx) if ray_dx else _FAR
    delta_y = abs(1.0 / ray_dy) if ray_dy else _FAR

    if ray_dx < 0:
        step_x, side_x = -1, (px - map_x) * delta_x
    else:
        step_x, side_x = 1, (map_x + 1 - px) * delta_x
    if ray_dy < 0:
        step_y, side_y = -1, (py - map_y) * delta_y
    else:
        step_y, side_y = 1, (map_y + 1 - py) * delta_y

    side = 0
    while True:
        if side_x < side_y:
            side_x += delta_x; map_x += step_x; side = 0
        else:
            side_y += delta_y; map_y += step_y; side = 1
        # Ran off the map without hitting a wall — treat as infinitely far.
        if not (0 <= map_y < len(grid) and 0 <= map_x < len(grid[0])):
            return _FAR, side
        if grid[map_y][map_x] == 1:
            break

    # Perpendicular distance along the ray's primary axis (the side we just stepped).
    if side == 0:
        dist = (map_x - px + (1 - step_x) / 2) / ray_dx
    else:
        dist = (map_y - py + (1 - step_y) / 2) / ray_dy
    return abs(dist), side


class FirstPersonVisualizer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface

    def draw(self, grid, player: Player) -> None:
        # Renders one first-person frame by casting a ray per screen column.
        w, h = self.surface.get_size()
        # Stand in the centre of the tile, not its corner.
        px, py = player.location[0] + 0.5, player.location[1] + 0.5
        dir_x, dir_y = _DIR_VEC[player.facing]
        # Camera plane is dir rotated -90 degrees and scaled to the FOV.
        plane_x, plane_y = dir_y * FOV, -dir_x * FOV

        # Cheap flat ceiling/floor fill; replace with gradients/textures later.
        self.surface.fill(CEILING, (0, 0, w, h // 2))
        self.surface.fill(FLOOR,   (0, h // 2, w, h - h // 2))

        for col in range(w):
            camera_x = 2.0 * col / w - 1.0          # -1 (left) .. +1 (right)
            ray_dx = dir_x + plane_x * camera_x
            ray_dy = dir_y + plane_y * camera_x

            dist, side = _cast_column(grid, px, py, ray_dx, ray_dy)
            if dist >= _FAR or dist <= 0:
                continue                            # nothing to draw this column

            line_h = int(h / dist)                  # closer wall => taller slice
            y0 = max(0, h // 2 - line_h // 2)
            y1 = min(h, h // 2 + line_h // 2)
            color = WALL_EW if side == 1 else WALL_NS
            pygame.draw.line(self.surface, color, (col, y0), (col, y1))
