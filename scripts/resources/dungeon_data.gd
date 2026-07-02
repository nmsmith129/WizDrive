class_name DungeonData
extends Resource
## A whole dungeon: a name plus its ordered floors. Replaces the
## (name, numFloors, [FloorData, ...]) tuple returned by load_map_file().
## numFloors is implicit in floors.size().

@export var display_name: String = ""
@export var floors: Array[FloorData] = []
