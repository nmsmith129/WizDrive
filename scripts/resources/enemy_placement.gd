class_name EnemyPlacement
extends Resource
## One enemy positioned on a floor. Mirrors the two .dngn enemy line forms:
##   [ENEMY|name|px py]                 -> stats resolved from the EnemyType library
##   [ENEMY|name|hp|attack|speed|px py] -> explicit stat overrides
## A negative override means "use the library value". XP is never overridden
## (always sourced from the EnemyType), matching the Python convention.

@export var type_name: String = ""
@export var position: Vector2i = Vector2i.ZERO

@export var hp_override: int = -1
@export var attack_override: int = -1
@export var speed_override: int = -1
