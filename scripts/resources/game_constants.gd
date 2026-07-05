class_name GameConstants
extends Resource
## Container for static constants used by the entire game.

const FOURWAY : Array[Vector2i] = [
    Vector2i(0, 1),
    Vector2i(1, 0),
    Vector2i(0, -1),
    Vector2i(-1, 0),
]
const EIGHTWAY : Array[Vector2i] = [
    Vector2i(0, 1),
    Vector2i(1, 0),
    Vector2i(0, -1),
    Vector2i(-1, 0),
    Vector2i(1, 1),
    Vector2i(1, -1),
    Vector2i(-1, -1),
    Vector2i(-1, 1),
]