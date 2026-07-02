class_name GameConstants
extends RefCounted
## Shared enums and lookup tables for grid movement.
##
## Mirrors the Python `_FORWARD_DELTAS` / `_BACKWARD_DELTAS` dicts from player.py,
## but keyed by an enum instead of facing strings. Grid convention is preserved
## from the Python codebase: grid[y][x] with y=0 at the BOTTOM (math orientation),
## north = +y, east = +x. In 3D the grid y-axis maps to world -z (see FloorView3D).

enum Facing { NORTH, EAST, SOUTH, WEST }

## Indexed by Facing. One tile "forward" for a given facing.
const FORWARD: Array[Vector2i] = [
	Vector2i(0, 1),   # NORTH
	Vector2i(1, 0),   # EAST
	Vector2i(0, -1),  # SOUTH
	Vector2i(-1, 0),  # WEST
]

## Indexed by Facing. One tile "backward" (opposite of FORWARD).
const BACKWARD: Array[Vector2i] = [
	Vector2i(0, -1),  # NORTH
	Vector2i(-1, 0),  # EAST
	Vector2i(0, 1),   # SOUTH
	Vector2i(1, 0),   # WEST
]

## Case-insensitive parse of a facing token ("N"/"north"/"NORTH" ...).
## Used by the .dngn converter; returns Facing.NORTH for anything unrecognised.
static func facing_from_string(token: String) -> Facing:
	match token.strip_edges().to_upper():
		"N", "NORTH": return Facing.NORTH
		"E", "EAST": return Facing.EAST
		"S", "SOUTH": return Facing.SOUTH
		"W", "WEST": return Facing.WEST
		_: return Facing.NORTH


static func facing_to_string(facing: Facing) -> String:
	return ["north", "east", "south", "west"][facing]
