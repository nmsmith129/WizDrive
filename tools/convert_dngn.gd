extends SceneTree
## One-time importer: parses every .dngn file under SRC_DIR and writes an
## equivalent DungeonData .tres under OUT_DIR, then the .dngn format can be
## retired. Faithful port of map_loader.py's parsing, including the row reversal
## (file rows are top-to-bottom; internal grid has y=0 at the bottom) and the
## fact that object/player COORDINATES are already in the y=0-bottom convention.
##
## Run headless from the repo root:
##   godot --headless --path . --script res://tools/convert_dngn.gd
## Enemy xp / item category+effect are NOT stored here; they resolve at runtime
## via TypeLibrary.

const SRC_DIR := "res://archive/assets/maps"
const OUT_DIR := "res://data/maps"


func _initialize() -> void:
	if not DirAccess.dir_exists_absolute(OUT_DIR):
		DirAccess.make_dir_recursive_absolute(OUT_DIR)
	var dir := DirAccess.open(SRC_DIR)
	if dir == null:
		push_error("convert_dngn: source dir not found: %s" % SRC_DIR)
		quit()
		return
	var count := 0
	for file_name in dir.get_files():
		if not file_name.ends_with(".dngn"):
			continue
		var src_path := SRC_DIR.path_join(file_name)
		var dungeon := _parse_file(src_path)
		if dungeon == null:
			continue
		var out_path := OUT_DIR.path_join(file_name.trim_suffix(".dngn") + ".tres")
		var err := ResourceSaver.save(dungeon, out_path)
		if err != OK:
			push_error("convert_dngn: save failed for %s (err %d)" % [out_path, err])
		else:
			print("convert_dngn: %s -> %s (%d floors)" % [file_name, out_path, dungeon.floors.size()])
			count += 1
	print("convert_dngn: converted %d dungeon(s)." % count)
	quit()


func _parse_file(path: String) -> DungeonData:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("convert_dngn: cannot open %s" % path)
		return null
	var raw: Array[String] = []
	while not f.eof_reached():
		raw.append(f.get_line())
	f.close()

	var non_empty: Array[String] = []
	for line in raw:
		if line.strip_edges() != "":
			non_empty.append(line)
	if non_empty.size() < 2:
		push_error("convert_dngn: %s too short (missing name/floor count)" % path)
		return null

	var dungeon := DungeonData.new()
	dungeon.display_name = non_empty[0].strip_edges()

	# Index in raw immediately after the 2nd non-empty line (the header).
	var seen := 0
	var after_header := raw.size()
	for i in raw.size():
		if raw[i].strip_edges() != "":
			seen += 1
			if seen == 2:
				after_header = i + 1
				break

	for block in _split_blocks(raw.slice(after_header)):
		var fd := _parse_block(block, path)
		if fd != null:
			dungeon.floors.append(fd)
	return dungeon


## Split lines into floor blocks using blank lines as separators (port of
## map_loader._split_floor_blocks).
func _split_blocks(lines: Array) -> Array:
	var blocks: Array = []
	var current: Array[String] = []
	for line in lines:
		if line.strip_edges() == "":
			if not current.is_empty():
				blocks.append(current)
				current = []
		else:
			current.append(line)
	if not current.is_empty():
		blocks.append(current)
	return blocks


func _parse_block(lines: Array, path: String) -> FloorData:
	var size := int(lines[0].strip_edges())
	if size <= 0:
		push_error("convert_dngn: %s bad floor size %s" % [path, lines[0]])
		return null

	var fd := FloorData.new()

	# S rows, top-to-bottom in file; reverse so grid[0] is the bottom row.
	var raw_rows: Array[PackedInt32Array] = []
	for i in size:
		var tokens: PackedStringArray = lines[1 + i].strip_edges().split(" ", false)
		var row := PackedInt32Array()
		for t in tokens:
			row.append(int(t))
		raw_rows.append(row)
	raw_rows.reverse()
	fd.grid = raw_rows

	# Player x y and facing (coords already in y=0-bottom convention).
	var pcoords := _coords(lines[1 + size])
	fd.player_start = pcoords
	fd.facing = GameConstants.facing_from_string(lines[2 + size])

	# Optional descriptor lines, any order.
	for j in range(3 + size, lines.size()):
		var obj: String = lines[j]
		if obj.begins_with("ENEMY|"):
			fd.enemies.append(_parse_enemy(obj))
		elif obj.begins_with("ITEM|"):
			fd.items.append(_parse_item(obj))
		elif obj.begins_with("STAIRS|"):
			fd.has_stairs = true
			fd.stairs = _coords(obj.split("|")[1])
		else:
			push_warning("convert_dngn: %s unrecognised line: %s" % [path, obj])
	return fd


## Parse a trailing "x y" fragment into a Vector2i.
func _coords(fragment: String) -> Vector2i:
	var parts := fragment.strip_edges().split(" ", false)
	return Vector2i(int(parts[0]), int(parts[1]))


## ENEMY|name|x y  OR  ENEMY|name|hp|attack|speed|x y
func _parse_enemy(line: String) -> EnemyPlacement:
	var parts := line.split("|")
	var p := EnemyPlacement.new()
	p.type_name = parts[1].strip_edges()
	if parts.size() == 3:
		p.position = _coords(parts[2])
	elif parts.size() == 6:
		p.hp_override = int(parts[2])
		p.attack_override = int(parts[3])
		p.speed_override = int(parts[4])
		p.position = _coords(parts[5])
	else:
		push_error("convert_dngn: bad ENEMY line: %s" % line)
	return p


## ITEM|name|x y  OR  ITEM|name|value|description|x y
func _parse_item(line: String) -> ItemPlacement:
	var parts := line.split("|")
	var p := ItemPlacement.new()
	p.type_name = parts[1].strip_edges()
	if parts.size() == 3:
		p.position = _coords(parts[2])
	elif parts.size() == 5:
		p.value_override = int(parts[2])
		p.description_override = parts[3]
		p.position = _coords(parts[4])
	else:
		push_error("convert_dngn: bad ITEM line: %s" % line)
	return p
