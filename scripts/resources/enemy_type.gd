class_name EnemyType
extends Resource
## A named enemy stat block. Port of an entry in enemy.py's ENEMY_TYPES dict.
## One .tres per enemy type lives in resources/enemies/. XP is intrinsic to the
## type and (per project convention) is always taken from here, never the map.

@export var display_name: String = ""
@export var hp: int = 10
@export var attack: int = 3
@export var speed: int = 1
@export var xp: int = 0
## Optional sprite/mesh shown when this enemy is instanced into a floor view.
@export var texture: Texture2D
