class_name TestRogueGenerator
extends RefCounted

var sectors := RogueGenerator.build_sectors()

func run(t : TestContext) -> void:
    t.check("RogueGenerator: there are 9 sectors", sectors.size() == 9)
    t.check("RogueGenerator: sectors[Vector2i(0, 0)] is Rect2i(0, 0, 15, 15)", sectors[Vector2i(0, 0)] == Rect2i(0, 0, 15, 15))
    t.check("RogueGenerator: sectors[Vector2i(2, 2)] is Rect2i(30, 30, 15, 15)", sectors[Vector2i(2, 2)] == Rect2i(30, 30, 15, 15))
    t.check("RogueGenerator: sectors do not overlap", overlap_check())

func overlap_check() -> bool:
    var values := sectors.values()
    for i in range(values.size()):
        for j in range(i+1, values.size()):
            if values[i].intersects(values[j]):
                return false
    return true