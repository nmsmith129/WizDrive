class_name PlayerData
extends Resource
## Serializable player state. Port of the attribute/XP fields on player.py's
## Player class. Behaviour (move/turn/strike) lives in player.gd, which wraps a
## PlayerData; keeping data in a Resource makes SaveGame persistence trivial.

@export var display_name: String = "Hero"
@export var location: Vector2i = Vector2i.ZERO
@export var facing: GameConstants.Facing = GameConstants.Facing.NORTH

## Chance to hit on a strike (0.5 = 50%).
@export var attack: float = 0.5
@export var strength: int = 1   # base melee damage, added to equipped weapon
@export var defense: int = 1    # subtracted from incoming damage (floored at 1)
@export var max_hp: int = 10
@export var intelligence: int = 1  # spell effectiveness (unused until spells exist)
@export var mana: int = 1          # maximum mana

@export var hp: int = 10
@export var mp: int = 1
@export var xp: int = 0
@export var level: int = 1

## Item type_names collected from floors; equipment/usage systems come later.
@export var inventory: Array[String] = []
