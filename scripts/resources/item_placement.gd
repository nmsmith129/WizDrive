class_name ItemPlacement
extends Resource
## One item lying on a floor. Mirrors the two .dngn item line forms:
##   [ITEM|name|px py]                       -> value/description from the ItemType library
##   [ITEM|name|value|description|px py]      -> explicit value/description override
## category and effect always come from the ItemType library by name.
## A negative value_override / empty description_override means "use the library value".

@export var type_name: String = ""
@export var position: Vector2i = Vector2i.ZERO

@export var value_override: int = -1
@export_multiline var description_override: String = ""
