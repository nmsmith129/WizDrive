## A rectangular room: its footprint on the grid and what kind of room it is

class_name Room
extends Resource

enum Kind { STANDARD, ENTRANCE, EXIT }

@export var rect : Rect2i
@export var kind : Kind = Kind.STANDARD