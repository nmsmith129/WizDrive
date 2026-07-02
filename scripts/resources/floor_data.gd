class_name FloorData
extends Resource
## One dungeon floor. Named-field replacement for the positional Python
## `FloorData` tuple (grid, playerPos, facing, enemies, items, stairs).
##
## `grid` rows follow the INTERNAL convention (y=0 at the bottom): grid[y][x],
## 0 = open, 1 = wall. The converter reverses the top-to-bottom .dngn rows on
## import, exactly as map_loader.load_map_text did.

@export var grid: Array[PackedInt32Array] = []
@export var player_start: Vector2i = Vector2i.ZERO
@export var facing: GameConstants.Facing = GameConstants.Facing.NORTH
@export var enemies: Array[EnemyPlacement] = []
@export var items: Array[ItemPlacement] = []

## Vector2i has no null, so guard stairs presence with this flag.
@export var has_stairs: bool = false
@export var stairs: Vector2i = Vector2i.ZERO

## Grid is square (S x S); returns S.
func size() -> int:
	return grid.size()

func is_wall(x: int, y: int) -> bool:
	var s := size()
	if x < 0 or y < 0 or x >= s or y >= s:
		return true
	return grid[y][x] == 1
