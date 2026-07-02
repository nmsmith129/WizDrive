class_name ItemType
extends Resource
## A named item stat block. Port of an entry in item.py's ITEM_TYPES dict.
## `effect` replaces the NotRequired TypedDict fields (strength/heal); use an
## untyped Dictionary so future effect kinds don't require a schema change.

@export var display_name: String = ""
@export var value: int = 1
## "weapon" | "armor" | "consumable" | "treasure" | "misc"
@export var category: String = "misc"
@export_multiline var description: String = ""
## Category-specific bonuses, e.g. {"strength": 4} or {"heal": 15}.
@export var effect: Dictionary = {}
@export var texture: Texture2D
