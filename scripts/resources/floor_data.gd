class_name FloorData
extends Resource

@export var grid : Array[PackedInt32Array]

func wall_tiles() -> Array[Vector2i]:
    var walls : Array[Vector2i] = []
    for y in range(size()):
        for x in range(size()):
            if is_wall(x, y):
                walls.append(Vector2i(x, y))
    return walls

func size() -> int:
    return grid.size()

func is_wall(x : int, y : int) -> bool:
    if x < 0 or y < 0 or x >= size() or y >= size():
        return true
    return grid[y][x] == 1