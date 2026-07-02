extends SceneTree
## One-time generator: writes the EnemyType / ItemType .tres library files from
## the data ported out of enemy.py (ENEMY_TYPES) and item.py (ITEM_TYPES).
##
## Run headless from the repo root:
##   godot --headless --path . --script res://tools/generate_types.gd
## Safe to re-run; it overwrites the generated .tres files. TypeLibrary picks
## them up on the next launch.

const ENEMY_DIR := "res://resources/enemies"
const ITEM_DIR := "res://resources/items"

# name -> [hp, attack, speed, xp]  (from enemy.py ENEMY_TYPES)
const ENEMIES := {
	"Rat":       [4, 1, 1, 5],
	"Spider":    [6, 2, 1, 10],
	"Goblin":    [10, 3, 1, 15],
	"Skeleton":  [15, 4, 1, 20],
	"Zombie":    [18, 4, 1, 25],
	"Troll":     [20, 5, 1, 30],
	"Dark Mage": [12, 6, 1, 35],
	"Orc":       [25, 6, 1, 40],
	"Wraith":    [8, 7, 1, 45],
	"Vampire":   [22, 8, 1, 50],
	"Dragon":    [50, 15, 1, 100],
}

# name -> {value, category, description, effect}  (from item.py ITEM_TYPES)
const ITEMS := {
	"Gold Coin":      {"value": 5, "category": "treasure", "description": "A shiny gold coin", "effect": {}},
	"Ancient Scroll": {"value": 50, "category": "treasure", "description": "Inscribed with an unknown spell", "effect": {}},
	"Iron Key":       {"value": 5, "category": "misc", "description": "Opens a locked door somewhere", "effect": {}},
	"Health Potion":  {"value": 20, "category": "consumable", "description": "Restores 15 HP", "effect": {"heal": 15}},
	"Mana Potion":    {"value": 20, "category": "consumable", "description": "Restores spent mana", "effect": {"heal": 0}},
	"Dagger":         {"value": 15, "category": "weapon", "description": "A small, quick blade", "effect": {"strength": 2}},
	"Iron Sword":     {"value": 30, "category": "weapon", "description": "A sturdy iron blade", "effect": {"strength": 4}},
	"Battle Axe":     {"value": 55, "category": "weapon", "description": "A heavy two-handed axe", "effect": {"strength": 7}},
	"Leather Armor":  {"value": 25, "category": "armor", "description": "Light protective hide", "effect": {}},
}


func _initialize() -> void:
	_ensure_dir(ENEMY_DIR)
	_ensure_dir(ITEM_DIR)

	for name in ENEMIES:
		var stats: Array = ENEMIES[name]
		var e := EnemyType.new()
		e.display_name = name
		e.hp = stats[0]
		e.attack = stats[1]
		e.speed = stats[2]
		e.xp = stats[3]
		_save(e, ENEMY_DIR.path_join("%s.tres" % _slug(name)))

	for name in ITEMS:
		var d: Dictionary = ITEMS[name]
		var it := ItemType.new()
		it.display_name = name
		it.value = d["value"]
		it.category = d["category"]
		it.description = d["description"]
		it.effect = d["effect"]
		_save(it, ITEM_DIR.path_join("%s.tres" % _slug(name)))

	print("generate_types: wrote %d enemy + %d item resources." % [ENEMIES.size(), ITEMS.size()])
	quit()


func _ensure_dir(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		DirAccess.make_dir_recursive_absolute(path)


func _slug(name: String) -> String:
	return name.to_lower().replace(" ", "_")


func _save(res: Resource, path: String) -> void:
	var err := ResourceSaver.save(res, path)
	if err != OK:
		push_error("generate_types: failed to save %s (err %d)" % [path, err])
