class_name RogueGenerator
extends RefCounted

const MAP_SIZE : Vector2i = Vector2i(45, 45)
const GRID : int = 3
const SECTOR_SIZE : Vector2i = MAP_SIZE / GRID
const ROOM_MIN : int = 4

## Creates a RandomNumberGenerator with an explicit seed, so maps are reproducible.
## r_seed: the seed value; the same seed always regenerates the same dungeon.
static func _make_rng(r_seed : int) -> RandomNumberGenerator:
    var random = RandomNumberGenerator.new()
    random.seed = r_seed
    return random


## Divides the map into Rogue's 3x3 grid of sectors, each holding at most one room.
## Confining every room to its own sector is what makes overlap tests unnecessary.
## Returns: sector coord (col, row) -> that sector's tile bounds.
static func build_sectors() -> Dictionary[Vector2i, Rect2i]:
    var sectors : Dictionary[Vector2i, Rect2i] = {}
    for y in range(GRID):
        for x in range(GRID):
            var pos : Vector2i = Vector2i(x * SECTOR_SIZE.x, y * SECTOR_SIZE.y)
            sectors[Vector2i(x, y)] = Rect2i(pos, SECTOR_SIZE)
    return sectors

## Places one randomly sized room per sector, inset to keep a >= 1 tile margin between the
## room's wall ring and the sector edge, so corridors always have somewhere to run.
## sectors: sector coord -> tile bounds, from build_sectors().
## randgen: seeded RNG; the caller owns the seed so a given seed reproduces the layout.
## Returns: sector coord -> the Room placed in it.
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

## Paints the rooms into a tile grid: fills everything with wall, then carves each room's
## interior to floor. A Room's rect includes its wall ring, so only rect.grow(-1) is carved
## and the ring is simply left as the wall it already was.
## rooms: sector coord -> Room, from build_rooms().
## Returns: a FloorData whose grid is 0 = floor, 1 = wall.
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

## Builds the 4-way neighbour graph over the sector grid - every border a corridor could
## later be carved along. Deterministic by design: which sectors touch is pure structure,
## not a random choice. Picking which of these borders become corridors happens in
## build_tree(). The sectors dict lookup doubles as the off-grid bounds check.
## sectors: sector coord -> tile bounds, from build_sectors().
## Returns: sector coord -> array of neighbouring sector coords.
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

## Picks a randomized spanning tree over the sector graph, guaranteeing every room is
## reachable. Grows one connected blob outward: each pass gathers every edge leading out of
## the blob and takes one at random. Deliberately not a random walk - a walk only extends
## from where it currently stands and can strand sectors. Yields exactly one edge fewer
## than there are sectors, with no cycles.
## adjacency: sector coord -> neighbours, from build_adjacency().
## randgen: seeded RNG.
## Returns: array of [a, b] sector-coord pairs to carve corridors between.
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

## Picks a few edges the spanning tree did not use, adding loops so the dungeon has
## redundant routes instead of exactly one path between any two rooms. Mirrors Rogue's
## rnd(5) extra passages in passages.c.
## Edges are unordered pairs - [a, b] and [b, a] are the same corridor - which is why the
## inverse is checked both when pruning tree edges and when de-duplicating candidates.
## tree: the spanning tree's edges, from build_tree().
## adjacency: sector coord -> neighbours, from build_adjacency().
## randgen: seeded RNG.
## Returns: array of extra [a, b] pairs only; the tree's own edges are not repeated.
static func build_loop_tree(tree : Array, adjacency : Dictionary[Vector2i, Array],
        randgen : RandomNumberGenerator) -> Array:
    var return_array : Array = []
    var extra_edges : Array = []
    var edge_count : int = randgen.randi_range(0, 4)        # number of extra edges
    
    for coord in adjacency:
        for neighbor in adjacency[coord]:
            var edge := [coord, neighbor]
            var inverse := [neighbor, coord]
            if !tree.has(edge)  and !tree.has(inverse) and !extra_edges.has(inverse):
                extra_edges.append(edge)
    for new_edge in range(0, edge_count):
        var loop_edge : Array = extra_edges[randgen.randi_range(0, extra_edges.size()-1)]
        return_array.append(loop_edge)
        extra_edges.erase(loop_edge)
    return return_array

## Carves a straight run of floor between two points that share a row or column. The one
## double loop handles either axis: whichever coordinate p and q share collapses its range
## to a single value, so a fixed-x pair carves a vertical line and a fixed-y pair a horizontal
## one. Mutates the grid in place.
## floor_data: the FloorData to carve into (a Resource, so changes are visible to the caller).
## p, q: the segment endpoints; must be axis-aligned (equal x or equal y).
static func _carve_line(floor_data : FloorData, p : Vector2i, q : Vector2i) -> void:
    for x in range(min(p.x, q.x), max(p.x, q.x) + 1):
        for y in range(min(p.y, q.y), max(p.y, q.y) + 1):
            floor_data.grid[y][x] = 0
    return

## Carves an L-shaped corridor connecting two rooms' centres: one horizontal leg to the elbow,
## then one vertical leg to the far centre. The legs inside a room are already floor (harmless),
## so the corridor only really cuts through the wall ring and the gap between rooms - the
## opening it punches through the ring is the "door" until a distinct door tile type exists.
## floor_data: the FloorData to carve into.
## a, b: the two rooms to connect; order does not matter.
static func _carve_corridor(floor_data : FloorData, a : Room, b : Room) -> void:
    var ca : Vector2i = a.rect.get_center()
    var cb : Vector2i = b.rect.get_center()
    var elbow : Vector2i = Vector2i(cb.x, ca.y)
    _carve_line(floor_data, ca, elbow)
    _carve_line(floor_data, cb, elbow)
    return

## Carves every corridor into the grid. Tree and loop edges are treated identically - both are
## just [a, b] sector-coord pairs - so they are concatenated and carved in one pass.
## floor_data: the FloorData to carve into.
## tree: the spanning tree's edges, from build_tree().
## loop_tree: the extra loop edges, from build_loop_tree().
## rooms: sector coord -> Room, used to look up each edge's endpoints.
static func carve_corridors(floor_data : FloorData, tree : Array, loop_tree : Array,
        rooms : Dictionary[Vector2i, Room]) -> void:
    var edges : Array = tree + loop_tree
    for edge in edges:
        _carve_corridor(floor_data, rooms[edge[0]], rooms[edge[1]])
    return

static func generate(randgen : RandomNumberGenerator) -> FloorData:
    var sectors := build_sectors()
    var rooms := build_rooms(sectors, randgen)
    var floor_data := build_floor_data(rooms)
    var adjacency := build_adjacency(sectors)
    var tree := build_tree(adjacency, randgen)
    var loop_tree := build_loop_tree(tree, adjacency, randgen)
    carve_corridors(floor_data, tree, loop_tree, rooms)
    return floor_data