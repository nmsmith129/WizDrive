class_name Enemy
extends RefCounted
## Runtime enemy instance — the mutable, stat-bearing half of enemy.py's Enemy.
## (The pygame Sprite half becomes a scene node in Stage 3.) Usually built from
## an EnemyType library entry via from_type(); direct construction is for tests.

signal defeated  ## hp reached 0; GameState listens to award XP to the killer

var display_name: String
var hp: int          # current hit points; mutated during combat
var attack: int
var speed: int
var xp: int          # reward granted to the player on kill
var grid_pos: Vector2i


func _init(p_name := "", p_hp := 1, p_attack := 1, p_speed := 1, p_xp := 0, p_grid_pos := Vector2i.ZERO) -> void:
	# Direct construction with explicit stats (mirrors Enemy(...) in enemy.py).
	# Params use a p_ prefix so they don't shadow the member variables above.
	display_name = p_name
	hp = p_hp
	attack = p_attack
	speed = p_speed
	xp = p_xp
	grid_pos = p_grid_pos


static func from_type(type: EnemyType, pos: Vector2i) -> Enemy:
	# Build a runtime enemy from a library EnemyType. xp always comes from the
	# type — it is intrinsic to the enemy kind and never overridden per placement.
	return Enemy.new(type.display_name, type.hp, type.attack, type.speed, type.xp, pos)


func take_damage(amount: int) -> void:
	# Apply already-computed damage to hp; announce death so GameState awards XP.
	hp -= amount
	if hp <= 0:
		defeated.emit()


func _to_string() -> String:
	# Godot's str()/print() hook; mirrors enemy.py's __str__.
	return "%s (HP: %d, Attack: %d, Speed: %d, XP: %d)" % [display_name, hp, attack, speed, xp]
