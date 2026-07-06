class_name TestPathfinding
extends RefCounted

func run(t : TestContext) -> void:
    # build test, call, print/assert
    var size : int = 5
    var start : Vector2i = Vector2i(0, 0)
    var blocked: Array[Vector2i] = [
            Vector2i(2, 0), Vector2i(2, 1), Vector2i(2, 2), Vector2i(2, 3),  # wall, gap at y=4
    ]
    var dist : Dictionary = Pathfinding.dijkstra_map_4(start, blocked, size)

    t.check("4-way: start is 0", dist.get(start) == 0)
    t.check("4-way: wall tile absent", not dist.has(Vector2i(2, 1)))
    t.check("4-way: detour (4, 0) == 12", dist.get(Vector2i(4, 0)) == 12)

    dist = Pathfinding.dijkstra_map_8(start, blocked, size)

    t.check("8-way: start is 0", dist.get(start) == 0)
    t.check("8-way: wall tile absent", not dist.has(Vector2i(2, 1)))
    t.check("8-way: detour (4, 0) == 8", dist.get(Vector2i(4, 0)) == 8)
    return
