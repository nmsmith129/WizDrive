class_name RogueGenerator
extends RefCounted

const MAP_SIZE : Vector2i = Vector2i(45, 45)
const GRID : int = 3
const SECTOR_SIZE : Vector2i = MAP_SIZE / GRID
const ROOM_MIN : int = 4

static var rng : RandomNumberGenerator = _make_rng(12345)

static func _make_rng(r_seed : int) -> RandomNumberGenerator:
    var random = RandomNumberGenerator.new()
    random.seed = r_seed
    return random


static func build_sectors() -> Dictionary[Vector2i, Rect2i]:
    var sectors : Dictionary[Vector2i, Rect2i] = {}
    for y in range(GRID):
        for x in range(GRID):
            var pos : Vector2i = Vector2i(x * SECTOR_SIZE.x, y * SECTOR_SIZE.y)
            sectors[Vector2i(x, y)] = Rect2i(pos, SECTOR_SIZE)
    return sectors

static func build_rooms(sectors : Dictionary[Vector2i, Rect2i],
        randgen: RandomNumberGenerator) -> Dictionary[Vector2i, Room]:
    var rooms : Dictionary[Vector2i, Room] = {}
    for coord in sectors:
        var sector : Rect2i = sectors[coord]
        var w : int = randgen.randi_range(ROOM_MIN, sector.size.x - 2)
        var h : int = randgen.randi_range(ROOM_MIN, sector.size.y - 2)
        var offset_x : int = randgen.randi_range(1, sector.size.x - w - 1)
        var offset_y : int = randgen.randi_range(1, sector.size.y - h - 1)
        var room : Room = Room.new()
        var pos : Vector2i = sector.position + Vector2i(offset_x, offset_y)
        room.rect = Rect2i(pos, Vector2i(w, h))
        rooms[coord] = room
    return rooms

static func build_floor_data(rooms : Dictionary[Vector2i, Room]) -> FloorData:
    var this_floor : FloorData = FloorData.new()
    for y in range(MAP_SIZE.y):
        var row : PackedInt32Array = PackedInt32Array()
        row.resize(MAP_SIZE.x)
        row.fill(1)
        this_floor.grid.append(row)
    for room in rooms.values():
        var interior : Rect2i = room.rect.grow(-1)
        for y in range(interior.position.y, interior.end.y):
            for x in range(interior.position.x, interior.end.x):
                this_floor.grid[y][x] = 0
    return this_floor

static func build_adjacency(sectors : Dictionary[Vector2i, Rect2i]) -> Dictionary[Vector2i, Array]:
    var adjacency : Dictionary[Vector2i, Array] = {}
    for coord in sectors:
        var neighbors : Array[Vector2i] = []
        for direction in GameConstants.FOURWAY:
            var candidate : Vector2i = coord + direction
            if sectors.has(candidate):
                neighbors.append(candidate)
        adjacency[coord] = neighbors
    return adjacency

static func build_tree(adjacency : Dictionary[Vector2i, Array],
        randgen : RandomNumberGenerator) -> Array:
    var edges : Array = []
    var connected : Array[Vector2i] = []
    var frontier : Dictionary[Vector2i, Array] = adjacency.duplicate()
    var seed : Vector2i = frontier.keys()[randgen.randi_range(0, frontier.keys().size() - 1)]
    var candidates : Array
    connected.append(seed)
    frontier.erase(seed)
    while not frontier.is_empty():
        candidates = []
        for start_sec in connected:
            for end_sec in adjacency[start_sec]:
                if frontier.has(end_sec):
                    candidates.append([start_sec, end_sec])
        var winner : Array = candidates[randgen.randi_range(0, candidates.size() - 1)]
        connected.append(winner[1])
        frontier.erase(winner[1])
        edges.append(winner)

    return edges