extends Node
## Autoload singleton `TypeLibrary`. Runtime lookup of enemy/item stat blocks by
## name, replacing enemy.py's ENEMY_TYPES / get_stats and item.py's
## ITEM_TYPES / get_item_stats. Scans resources/enemies and resources/items for
## .tres files on startup and keys them by their display_name.

const ENEMY_DIR := "res://resources/enemies"
const ITEM_DIR := "res://resources/items"

var _enemies: Dictionary = {}  # display_name -> EnemyType
var _items: Dictionary = {}    # display_name -> ItemType


func _ready() -> void:
	_load_dir(ENEMY_DIR, _enemies)
	_load_dir(ITEM_DIR, _items)


func _load_dir(dir_path: String, into: Dictionary) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		push_warning("TypeLibrary: directory not found (run the type generator?): %s" % dir_path)
		return
	for file_name in dir.get_files():
		# In exported builds .tres becomes .tres.remap; load() handles the base path.
		if not (file_name.ends_with(".tres") or file_name.ends_with(".res") or file_name.ends_with(".remap")):
			continue
		var res_path := dir_path.path_join(file_name.trim_suffix(".remap"))
		var res := load(res_path)
		if res is Resource and "display_name" in res and res.display_name != "":
			into[res.display_name] = res


## Returns the EnemyType for `name`, or a generic fallback matching Python's
## get_stats default (hp 10, attack 3, speed 1, xp 0) for unknown names.
func get_enemy_type(name: String) -> EnemyType:
	if _enemies.has(name):
		return _enemies[name]
	var fallback := EnemyType.new()
	fallback.display_name = name
	return fallback  # EnemyType defaults already are 10/3/1/0


## Returns the ItemType for `name`, or a generic misc fallback matching Python's
## get_item_stats default (value 1, category "misc", empty description).
func get_item_type(name: String) -> ItemType:
	if _items.has(name):
		return _items[name]
	var fallback := ItemType.new()
	fallback.display_name = name
	return fallback  # ItemType defaults already are value 1, "misc", ""
