class_name TestFloorData
extends RefCounted

func run(t : TestContext) -> void:
    var test_data : FloorData = FloorData.new()
    test_data.grid = [
        PackedInt32Array([0, 0, 1, 0, 0]),
        PackedInt32Array([0, 1, 1, 0, 0]),
        PackedInt32Array([0, 0, 1, 0, 0]),
        PackedInt32Array([1, 0, 0, 0, 1]),
        PackedInt32Array([1, 1, 1, 1, 1]),
    ]

    t.check("FloorData: wall_tiles contains (1, 1)", Vector2i(1, 1) in test_data.wall_tiles())
    t.check("FloorData: (0, 5) is a wall", test_data.is_wall(0, 5) == true)
    t.check("FloorData: (3, 0) is not a wall", test_data.is_wall(3, 0) == false)
    return