class_name RogueGenerator
extends RefCounted

const MAP_SIZE : Vector2i = Vector2i(45, 45)
const GRID : int = 3
const SECTOR_SIZE : Vector2i = MAP_SIZE / GRID

static func build_sectors() -> Dictionary[Vector2i, Rect2i]:
    var sectors : Dictionary[Vector2i, Rect2i] = {}
    for y in range(GRID):
        for x in range(GRID):
            var pos : Vector2i = Vector2i(x * SECTOR_SIZE.x, y * SECTOR_SIZE.y)
            sectors[Vector2i(x, y)] = Rect2i(pos, SECTOR_SIZE)
    return sectors