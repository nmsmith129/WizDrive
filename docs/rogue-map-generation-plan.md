# Rogue Map Generation Plan

A working plan for WizDrive's **first** map generator, recreating the algorithm from the
original *Rogue* (`rooms.c`). Chosen over the SPD method (see
[SPD-map-generation-plan.md](SPD-map-generation-plan.md)) because it is markedly simpler to
implement while still producing a real, connected dungeon. The generator data types
(`Room`, `FloorData`) are shared; only the *algorithm* differs, so this method can be
swapped for SPD's later without touching the data classes.

## The algorithm in one picture

Rogue divides the map into a **3×3 grid of nine sectors** and drops **one room per
sector**, then connects neighbouring sectors with corridors.

```
+--------+--------+--------+
| room 0 | room 1 | room 2 |
+--------+--------+--------+
| room 3 | room 4 | room 5 |
+--------+--------+--------+
| room 6 | room 7 | room 8 |
+--------+--------+--------+
```

## Map dimensions: 45 × 45

Rogue targeted an 80×24 terminal, of which the dungeon was **80 × 22** (row 0 = messages,
row 23 = status). But terminal cells are ~2:1 tall, so 80×22 rendered roughly square;
drawn with **square graphic tiles** it would look very wide and flat (≈3.6:1).

We instead use **45 × 45**, chosen to keep *both* Rogue's density and a square canvas:

- **Square** on screen with square tiles, suited to a scrolling, camera-follow view
  (the Android target especially).
- **Divides cleanly** into a 3×3 grid of **exactly 15×15 sectors** — no leftover
  columns/rows to distribute.
- **~2,025 tiles**, close to Rogue's ~1,760, so nine rooms + corridors keeps Rogue's
  sparse, tight rhythm. Rooms stay small (≈4–12 wide) rather than ballooning to fill a
  large sector.

HUD (message log, status) lives in Godot UI *outside* the `FloorData` grid — the same
separation Rogue had, just drawn with UI nodes instead of reserved terminal rows.

**Performance note:** `Pathfinding` currently does `neighbor in blocked` against an
`Array[Vector2i]` — an O(n) scan per neighbor, so the connectivity backstop scales ~
quadratically with map area. At 45×45 this is a non-issue; if the map ever grows much
larger, switch the blocked-list to a `Dictionary`/set for O(1) lookups first.

Two properties make this much simpler than accretion-based generators:

- **No overlap logic.** Each room is confined to its own sector, so rooms *physically
  cannot* collide. No overlap tests, no placement retries.
- **Connectivity is structural.** The nine sectors form a known grid graph, so connecting
  rooms is "join adjacent sectors," not a search. A randomized spanning tree guarantees
  every room is reachable; a few extra edges add loops.

## How it fits what already exists

- `FloorData.grid` is `Array[PackedInt32Array]`, indexed `grid[y][x]`, `0 = open, 1 = wall`.
  The generator produces that nested array and wraps it in a `FloorData`.
- `Room` (`scripts/resources/room.gd`) is a shared data class: a `Rect2i` footprint plus a
  `RoomKind`. Generator-agnostic — Rogue and SPD both emit `Room`s.
- `Pathfinding.dijkstra_map_4(entrance, blocked, size)` floods from the entrance and serves
  as the **connectivity backstop** — assert every open tile is reachable. Rogue's structure
  means this should essentially always pass; it exists to catch corridor/painter bugs.

## Folder layout

| Kind of thing | Where | Base class |
|---|---|---|
| Data — `FloorData`, `Room` (shared by all generators) | `scripts/resources/` | `Resource` |
| Generator logic — one per algorithm (`rogue_generator.gd`) | `scripts/mapgen/` | `RefCounted`, `static func`s |

Generators are stateless logic, not `Resource`s, so they live in `scripts/mapgen/`, not
`scripts/resources/`.

## Build steps (vertical slice — always keep it runnable)

1. **`Room` data class** — ✅ done, lives in `scripts/resources/room.gd`.
2. **Sector layout** — split the map into a 3×3 grid; compute each sector's `Rect2i`
   bounds. At 45×45 these are exactly nine 15×15 sectors — no remainder to handle.
   Store them 2D as a **`Dictionary[Vector2i, Rect2i]` keyed by `(col, row)`** (GDScript
   can't nest typed arrays, and a coord-keyed dict makes step 5's adjacency trivial). This
   mirrors `Pathfinding`'s existing `Dictionary[Vector2i, int]` usage.
3. **Place rooms** — one random `Room` per sector: random width/height (above a minimum)
   at a random position *inside* the sector, leaving a margin so room walls don't touch
   the sector edge.
4. **Paint rooms** — stamp each room into a `FloorData` grid: interior floor `0`, a wall
   ring `1`. Everything outside rooms starts as wall.
5. **Corridors** — connect adjacent sectors' rooms. Build a graph over the 3×3 grid; carve
   a randomized spanning tree so all rooms connect, then add a couple of extra edges for
   loops. Corridors are L-shaped passages between facing walls, with a door where a
   corridor meets a room.
   - Adjacency uses the coord-keyed sector dict: for a sector at `(col, row)`, its
     neighbours are `coord + dir` for `dir in GameConstants.FOURWAY`, kept only when
     `sectors.has(coord + dir)` — the dict lookup *is* the bounds check. Same direction
     table `Pathfinding` uses on the tile grid.
6. **Connectivity backstop** — run `dijkstra_map_4` from an entrance; if any open tile is
   unreachable, regenerate (retry loop).
7. **Seed the RNG** — `RandomNumberGenerator` with an explicit seed, so maps are
   reproducible and testable.

## Deferred (not needed for the first generator)

- **"Gone rooms"** — Rogue occasionally replaces a room with a single passage junction
  (dark/maze rooms). Skip until the basic version works.
- **Tile types beyond floor/wall.** The first generator needs only two types, so binary
  `0/1` is enough. Once a painter paints a *second walkable type* (water, grass),
  `FloorData` grows a tile-type enum (`FLOOR = 0, WALL = 1`, then more), and `is_wall`
  splits into *type* vs *passability*. `grid` is `@export`ed (saved), so keeping
  `FLOOR = 0, WALL = 1` fixed keeps existing grids readable. Change of interpretation, not
  storage — `grid` already holds `0..N`.

## Testing

Add tests to the DIY runner (`tests/test_main.gd`) as each step lands:

- Sectors: the 3×3 bounds tile the map without overlapping.
- Placement: each room's `Rect2i` sits within its sector's bounds.
- Painting: room interiors are open (`0`), the surrounding ring is wall (`1`).
- Connectivity: `dijkstra_map_4` from the entrance reaches every open tile.

Run headless (note: `godot_console.exe`, not `godot.exe`):

```powershell
godot_console --headless --path . --script res://tests/test_main.gd
```
