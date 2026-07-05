extends SceneTree

var _passed : int = 0
var _failed : int = 0

func _initialize() -> void:
    _test_pathfinding()
    print("\n%d passed, %d failed" % [_passed, _failed])
    quit(1 if _failed > 0 else 0)

func check(label: String, ok: bool) -> void:
    if ok:
        _passed += 1
    else:
        _failed += 1
        print("FAIL: ", label)
    


func _test_pathfinding() -> void:
    # build test, call, print/assert
    var size : int = 5
    var start : Vector2i = Vector2i(0, 0)
    var blocked: Array[Vector2i] = [
            Vector2i(2, 0), Vector2i(2, 1), Vector2i(2, 2), Vector2i(2, 3),  # wall, gap at y=4
    ]
    var dist : Dictionary = Pathfinding.dijkstra_map_4(start, blocked, size)

    check("4-way: start is 0", dist.get(start) == 0)
    check("4-way: wall tile absent", not dist.has(Vector2i(2, 1)))
    check("4-way: detour (4, 0) == 12", dist.get(Vector2i(4, 0)) == 12)

    dist = Pathfinding.dijkstra_map_8(start, blocked, size)

    check("8-way: start is 0", dist.get(start) == 0)
    check("8-way: wall tile absent", not dist.has(Vector2i(2, 1)))
    check("8-way: detour (4, 0) == 8", dist.get(Vector2i(4, 0)) == 8)
    return
