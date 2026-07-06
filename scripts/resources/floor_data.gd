class_name FloorData
extends Resource

@export var grid : Array[PackedInt32Array]

func wall_tiles() -> Array[Vector2i]:
    var walls : Array[Vector2i] = []
    for x in range(size()[0]):
        for y in range(size()[1]):
            if is_wall(Vector2i(x, y)):
                walls.append(Vector2i(x, y))
    return walls

func tile_at(grid_pos : Vector2i) -> int:
    return grid[grid_pos[1]][grid_pos[0]]

func size() -> Vector2i:
    if grid.is_empty():
        return Vector2i.ZERO
    return Vector2i(grid[0].size(), grid.size())

func is_wall(grid_pos : Vector2i) -> bool:
    var x : int = grid_pos[0]
    var y : int = grid_pos[1]
    if x < 0 or y < 0 or x >= size().x or y >= size().y:
        return true
    return tile_at(grid_pos) == 1