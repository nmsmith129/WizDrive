extends SceneTree

var _passed : int = 0
var _failed : int = 0
var _ran : bool = false

func _process(_delta: float) -> bool:
    if _ran:
        return true
    _ran = true
    _run_tests()                                   # all your check(...) calls
    print("%d passed, %d failed" % [_passed, _failed])
    quit(1 if _failed > 0 else 0)                   # sets the exit code
    return true 

func _run_tests() -> void:
    var test_data : FloorData = FloorData.new()
    test_data.grid = [
        PackedInt32Array([0, 0, 1, 0, 0]),
        PackedInt32Array([0, 1, 1, 0, 0]),
        PackedInt32Array([0, 0, 1, 0, 0]),
        PackedInt32Array([1, 0, 0, 0, 1]),
        PackedInt32Array([1, 1, 1, 1, 1]),
    ]
    var wall_tiles : Array[Vector2i] = test_data.wall_tiles()

    check("FloorData: wall_tiles contains (1, 1)", Vector2i(1, 1) in test_data.wall_tiles())
    check("FloorData: (0, 5) is a wall", test_data.is_wall(0, 5) == true)
    check("FloorData: (3, 0) is not a wall", test_data.is_wall(3, 0) == false)
    return

func check(label: String, ok: bool) -> void:
    if ok:
        _passed += 1
    else:
        _failed += 1
        print("FAIL: ", label)
    return

func _initialize() -> void:
    return