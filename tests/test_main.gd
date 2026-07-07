extends SceneTree

func _initialize() -> void:
    var t := TestContext.new()
    TestFloorData.new().run(t)
    TestPathfinding.new().run(t)
    TestRogueGenerator.new().run(t)
    print("\n%d passed, %d failed" % [t.passed, t.failed])
    quit(1 if t.failed > 0 else 0)
