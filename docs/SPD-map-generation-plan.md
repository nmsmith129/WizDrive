# Map Generation Plan

## Summary of the Shattered Pixel Dungeon algorithm

For reference, this is how *Shattered Pixel Dungeon* actually builds a level (`Level`,
`RegularLevel`, the `Builder` classes, and the `Painter`s). Its defining trait is a clean
split between **layout** (an abstract graph of rooms and doors) and **painting** (turning
that graph into tiles). WizDrive's plan below adopts that split; this section is the source
material. (The "Guiding idea" section further down frames how we borrow from it.)

1. **Rooms are first-class objects.** A level is assembled from `Room` objects, each with a
   *type* and its own behaviour, and each declaring a min/max size. Broad categories:
   **entrance** and **exit**, **standard** rooms (fill the level), **special** rooms (shops,
   treasuries, vaults, gardens… — depth-gated and quota-limited), **secret** rooms, and
   **connection** rooms (tunnels/junctions).
2. **Choose the room set (`initRooms`).** Pick one entrance and one exit, a depth-scaled
   number of standard rooms, a limited number of special/secret rooms, and some connection
   rooms — before any geometry is decided.
3. **A `Builder` arranges rooms into a connected graph.** `RegularLevel` uses
   **`LoopBuilder`**:
   - Place the entrance, then lay a subset of standard rooms in a **large loop/ring** around
     it, spacing them by angle so the loop closes back on itself.
   - Hang the remaining rooms (specials, extra standards) off the loop as **branches**.
   - Rooms attach **edge-to-edge (accretion)**: each new room is placed adjacent to an
     already-placed room, negotiating a shared edge and door position (`Room.connect`). If a
     room can't be placed without overlapping, the build **fails and retries**; after enough
     failures the whole level regenerates.
   - **Connectivity is guaranteed by construction** — a room only enters the graph by being
     connected to a room already in it. No flood-fill rejection needed for basic reachability.
4. **Doors record connections.** Each pair of adjacent, connected rooms gets a door of some
   kind (regular, locked, hidden/secret, barricade, empty). Connection/tunnel rooms bridge
   rooms that should link but sit too far apart.
5. **`Painter`s rasterize the graph (`RegularPainter`).** Only now does anything become
   tiles. The painter computes the bounding box, fills the map with wall/chasm, then calls
   **each room's own `paint()`** to stamp its floor, walls, water, grass, and traps —
   different room types paint differently. Doors are then painted between connected rooms.
6. **Organic detail + decoration.** Water and grass are laid down in blobs from a
   per-level noise/cellular pattern; traps, plants, and decorations are scattered.
7. **Populate and validate.** Place mobs and items, then verify the level is sound
   (e.g. entrance→exit reachable). If validation fails, discard and regenerate the whole
   level.

---

A working plan for WizDrive's first map generator. The **architecture target** is
Shattered Pixel Dungeon's *layout-then-paint* pipeline; the **first build** starts with
the simplest layout so we learn one new thing at a time.

## Guiding idea (borrowed from Shattered Pixel Dungeon)

> Separate **layout** (rooms + doors as an abstract graph) from **painting**
> (turning that graph into the tile grid).

SPD's real pipeline, for reference:

1. **Pick `Room` objects** — first-class objects with *types* (entrance, exit, standard,
   special, connection) and their own behavior. Each declares min/max size.
2. **A `Builder` arranges them into a connected graph** — the signature `LoopBuilder`
   lays the main rooms in a rough loop, then hangs extra rooms off it as branches.
   Rooms attach to each other's edges (accretion) until they fit; if they can't, the
   builder fails and the whole level regenerates.
3. **Doors connect adjacent rooms** — connectivity is guaranteed *by construction*, not
   by flood-fill rejection.
4. **`Painter`s rasterize** — each room type paints its own floor/walls/water/grass/traps
   into the tile grid; only now does anything become tiles.

In our project this repositions the existing `Pathfinding.dijkstra_map_4`: once layout
guarantees connectivity by construction, the Dijkstra flood becomes a **validation
backstop** (catch painter bugs) rather than the primary generate-reject mechanism.

## How it fits what already exists

- `FloorData.grid` is `Array[PackedInt32Array]`, indexed `grid[y][x]`, `0 = open, 1 = wall`.
  The generator's job is to produce that nested array and wrap it in a `FloorData`.
- `Pathfinding.dijkstra_map_4(entrance, wall_tiles, size)` floods from the entrance.
  Reject any layout where *reachable open-tile count ≠ total open-tile count* — the
  "no orphaned rooms" guarantee, essentially for free.
- Style: stateless `static func`s on a `RefCounted` (matching `Pathfinding`); data classes
  derive from `Resource` (matching `FloorData`); static typing throughout.

## Build steps (vertical slice — always keep it runnable)

1. **`Room` data class** (`extends Resource`) — a `Rect2i` plus a type enum. Just the struct.
   - Open question to settle here: does `Room` own its own painting method (very SPD),
     or does painting live in a separate `Painter` (cleaner separation to start)?
2. **Simple placement** — random non-overlapping room rects, returning a list of `Room`s
   plus a list of door/corridor connections. This is the `LoopBuilder`'s job in baby form.
3. **A `Painter`** — walk the rooms and connections and stamp `0`/`1` into a `FloorData`
   grid. This part survives even after a smarter builder replaces step 2.
4. **Connectivity backstop** — run `dijkstra_map_4` from an entrance; if any open tile is
   unreachable, throw the map away and regenerate (retry loop).
5. **Seed the RNG** — use `RandomNumberGenerator` with an explicit seed so maps are
   reproducible and testable.

## Later (growing into the SPD architecture)

- Replace step 2's random placement with a real `LoopBuilder` (main loop + branches).
- Give each room type its own painter for water / grass / special rooms.
- Room *types* with behavior: entrance, exit, shop/treasure/special, connection tunnels.

### Tile types (needed once painters paint flavor, not before)

The first generator only needs two types (floor, wall), so binary `0/1` is enough for
steps 1–4. The moment a painter paints a *second walkable type* (water, grass), `FloorData`
must grow tile types. This is a change of **interpretation**, not storage — `grid` is
already `Array[PackedInt32Array]` and can hold `0..N` today.

What changes when we get there:

- **A tile-type enum** — `enum Tile { FLOOR, WALL, WATER, GRASS, DOOR, ... }`. Keep
  `FLOOR = 0, WALL = 1` so existing grids stay valid.
- **Split "type" from "passability."** `is_wall` currently fuses them (`tile_at == 1`).
  Separate *what a tile is* (rendering/effects) from *does it block movement*
  (pathfinding). SPD's model: a `Terrain` id **plus** flag tables (`passable`,
  `losBlocking`, `flammable`…) indexed by type.
- **`wall_tiles()` → `impassable_tiles()`**, still feeding the `dijkstra_map_4` blocked
  list — pathfinding asks "is this passable," not "is this a wall."
- **Persistence note:** `grid` is `@export`ed, so it's saved with the game state. Changing
  the tile encoding touches save compatibility; keeping `FLOOR = 0, WALL = 1` fixed keeps
  existing grids readable when new types are added.

## Testing

Add tests to the existing DIY runner (`tests/test_main.gd`) as each step lands:

- Skeleton: generated grid has the requested size and is all walls.
- Rooms: room tiles are open (`0`), borders stay walls (`1`).
- Connectivity: `dijkstra_map_4` from the entrance reaches every open tile.

Run headless (note: `godot_console.exe`, not `godot.exe`):

```powershell
godot_console --headless --path . --script res://tests/test_main.gd
```
