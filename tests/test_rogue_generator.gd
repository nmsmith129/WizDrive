class_name TestRogueGenerator
extends RefCounted

var sectors := RogueGenerator.build_sectors()
var rooms := RogueGenerator.build_rooms(sectors, RogueGenerator.rng)
var floor_data := RogueGenerator.build_floor_data(rooms)
var adjacency := RogueGenerator.build_adjacency(sectors)
var tree := RogueGenerator.build_tree(adjacency, RogueGenerator.rng)
var loop_tree := RogueGenerator.build_loop_tree(tree, adjacency, RogueGenerator.rng)

func run(t : TestContext) -> void:
    RogueGenerator.carve_corridors(floor_data, tree, loop_tree, rooms)

    t.check("RogueGenerator: there are 9 sectors", sectors.size() == 9)
    t.check("RogueGenerator: sectors[Vector2i(0, 0)] is Rect2i(0, 0, 15, 15)", sectors[Vector2i(0, 0)] == Rect2i(0, 0, 15, 15))
    t.check("RogueGenerator: sectors[Vector2i(2, 2)] is Rect2i(30, 30, 15, 15)", sectors[Vector2i(2, 2)] == Rect2i(30, 30, 15, 15))
    t.check("RogueGenerator: sectors do not overlap", overlap_check())

    t.check("RogueGenerator: there are 9 rooms", rooms.size() == 9)
    t.check("RogueGenerator: rooms stay within their sectors", enclosure_check())
    t.check("RogueGenerator: Rooms meet minimum size requirements", size_check())
    
    t.check("RogueGenerator: interiors are floor", room_center_check())
    t.check("RogueGenerator: ring is wall", room_ring_check())

    t.check("RogueGenerator: adjacencies sum to 24", adjacency_check() == 24)

    t.check("RogueGenerator: there are eight edges in tree", tree.size() == 8)
    t.check("RogueGenerator: tree connects all sectors", tree_sector_check())
    t.check("RogueGenerator: loop tree and connecting tree do not share edges", loop_tree_check())
    t.check("RogueGenerator: map is fully connected", connectivity_check())

func overlap_check() -> bool:
    var values := sectors.values()
    for i in range(values.size()):
        for j in range(i+1, values.size()):
            if values[i].intersects(values[j]):
                return false
    return true

func enclosure_check() -> bool:
    for coord in sectors:
        if sectors[coord].encloses(rooms[coord].rect) == false:
            return false
    return true

func size_check() -> bool:
    for coord in rooms:
        if (rooms[coord].rect.size.x < RogueGenerator.ROOM_MIN
                or rooms[coord].rect.size.y < RogueGenerator.ROOM_MIN):
            return false
    return true

func room_center_check() -> bool:
    for room in rooms.values():
        if floor_data.tile_at(room.rect.get_center()) != 0:
            return false
    return true

func room_ring_check() -> bool:
    for room in rooms.values():
        if !floor_data.is_wall(room.rect.position):
            return false
    return true

func adjacency_check() -> int:
    var sum : int = 0
    for sector in adjacency:
        sum += adjacency[sector].size()
    return sum

func tree_sector_check() -> bool:
    var seen : Array[Vector2i] = []
    for edge in tree:
        seen.append(edge[0])
        seen.append(edge[1])
    for sector in sectors:
        if !seen.has(sector):
            return false
    return true

func loop_tree_check() -> bool:
    for node in tree:
        var inverse := [node[1], node[0]]
        if loop_tree.has(node) or loop_tree.has(inverse):
            return false
    return true

func connectivity_check() -> bool:
    var map_x : int = RogueGenerator.MAP_SIZE.x
    var map_y : int = RogueGenerator.MAP_SIZE.y
    var start : Vector2i = rooms.values()[0].rect.get_center()
    var tiles := floor_data.wall_tiles()
    var flood_count : int = Pathfinding.dijkstra_map_4(start, tiles, RogueGenerator.MAP_SIZE).size()
    var floor_count : int = map_x * map_y - tiles.size()
    return flood_count == floor_count