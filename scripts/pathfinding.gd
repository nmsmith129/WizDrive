class_name Pathfinding
extends RefCounted
## Pathfinding utility class for grid-based movement. Provides Dijkstra's algorithm to find
## the shortest path from a start position to a target position, considering obstacles
## and walkable tiles.


static func dijkstra_map_4(start : Vector2i, blocked : Array[Vector2i], size : int) -> Dictionary[Vector2i, int]:
    var open_set : Array[Vector2i] = [start]
    var score : Dictionary[Vector2i, int] = {start: 0}

    while open_set.size() > 0:
        var current : Vector2i = open_set.pop_front()
        var tentative_score = score[current] + 1
        for direction in GameConstants.FOURWAY:
            var neighbor : Vector2i = current + direction
            if neighbor.x < 0 or neighbor.x >= size:
                continue
            if neighbor.y < 0 or neighbor.y >= size:
                continue
            if neighbor in blocked or neighbor in score and score[neighbor] <= tentative_score:
                continue
            score[neighbor] = tentative_score
            open_set.append(neighbor)
    return score

static func dijkstra_map_8(start: Vector2i, blocked: Array[Vector2i], size : int) -> Dictionary[Vector2i, int]:
    var open_set: Array[Vector2i] = [start]
    var score: Dictionary[Vector2i, int] = {start: 0}

    while open_set.size() > 0:
        var current : Vector2i = open_set.pop_front()
        var tentative_score = score[current] + 1
        for direction in GameConstants.EIGHTWAY:
            var neighbor : Vector2i = current + direction
            if neighbor.x < 0 or neighbor.x >= size:
                continue
            if neighbor.y < 0 or neighbor.y >= size:
                continue
            if neighbor in blocked or neighbor in score and score[neighbor] <= tentative_score:
                continue
            score[neighbor] = tentative_score
            open_set.append(neighbor)
    return score