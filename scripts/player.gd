class_name Player
extends RefCounted
## Behavior/controller for the player, wrapping a PlayerData (data/behavior split).
## Ports player.py's Player. Combat is decoupled: strike() only ANNOUNCES outgoing
## damage (GameState applies it and owns kill/XP/counter); take_damage() applies
## incoming damage to self. Player never mutates other entities.

signal attacked(target: Enemy, amount: int)  ## I struck target, dealing `amount`
signal missed(target: Enemy)                 ## I swung and missed
signal damage_taken(amount: int)             ## I took `amount` damage
signal player_defeated                       ## my hp reached 0

var data: PlayerData


func _init(player_data: PlayerData = null) -> void:
	# Wrap the given PlayerData, or start a fresh default one.
	data = player_data if player_data != null else PlayerData.new()


func _to_string() -> String:
	# Godot's str()/print() hook; mirrors player.py's __str__.
	return "Player(name=%s, location=%s, hp=%d/%d, mp=%d/%d, attack=%s, strength=%d, defense=%d, intelligence=%d, xp=%d, level=%d)" % [
		data.display_name, data.location, data.hp, data.max_hp, data.mp, data.mana,
		data.attack, data.strength, data.defense, data.intelligence, data.xp, data.level,
	]


func pos_to(direction: GameConstants.Facing) -> Vector2i:
	# Tile one step in an absolute compass direction (peek only, no move).
	# Player does not consult its own facing; the caller (GameState) supplies
	# the absolute direction, so this serves both crawler and roguelike rules.
	return data.location + GameConstants.FORWARD[direction]


func move(direction: GameConstants.Facing) -> void:
	# Apply a one-tile move to self. GameState decides IF/where; Player just moves.
	data.location = pos_to(direction)


func turn_left() -> void:
	# Rotate facing 90 degrees counter-clockwise. +3 (mod 4) avoids negative modulo.
	data.facing = ((data.facing + 3) % 4) as GameConstants.Facing


func turn_right() -> void:
	# Rotate facing 90 degrees clockwise.
	data.facing = ((data.facing + 1) % 4) as GameConstants.Facing


func strike(enemy: Enemy) -> void:
	# Attacker side of a combat round: roll to hit and ANNOUNCE the outgoing damage.
	# Player never touches the enemy's hp — GameState applies the damage (via
	# enemy.take_damage) and owns kill/XP/counter-attack. Emit-only keeps it decoupled.
	if randf() < data.attack:
		var damage := data.strength  # + weapon bonus once equipment exists (stub: 0)
		attacked.emit(enemy, damage)
	else:
		missed.emit(enemy)


func take_damage(amount: int) -> void:
	# Defender side: apply an already-computed damage amount to hp. Defense
	# mitigation is the caller's (GameState's) job, per the decoupled combat model.
	data.hp -= amount
	damage_taken.emit(amount)
	if data.hp <= 0:
		player_defeated.emit()
