class_name ASCIIPrintout
extends RefCounted

static func _make_map() -> FloorData:
    var rng := RandomNumberGenerator.new()
    var new_map := RogueGenerator.generate(rng)
    return new_map

static func display_map() -> void:
    var map := _make_map()
    for y in range(map.size().y - 1, -1, -1):
        var mapline : String = ""
        for x in range(map.size().x):
            if map.grid[y][x] == 0:
                mapline += " "
            else:
                mapline += "#"
        print(mapline)
    return