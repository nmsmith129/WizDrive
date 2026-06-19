<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-persistence-schema-versioning/plan.md
<!-- SPECKIT END -->

# WizDrive — CLAUDE.md

> **Project memory** is kept in [`MEMORY.md`](MEMORY.md) at the repo root (shared on the network drive). Read it at the start of a session and record any cross-session context there — not in this file. This file is hand-maintained project documentation only.

WizDrive is a Python/Pygame dungeon crawler inspired by Wizardry. The project is in active early development: the core map system, entity classes, combat, XP/leveling, and player attribute systems are complete; first-person 3D rendering and most gameplay mechanics are still on the roadmap.

---

## Running the Game

### Visualizer Modes

The active visualizer is controlled by the `VISUALIZER` constant at the top of `wiz_drive_main.py`:

| Value | Mode | Notes |
|-------|------|-------|
| `0` | Pygame top-down (default) | Real-time, requires a display (WASD + Q) |
| `1` | Text/terminal | Real-time keypresses via `msvcrt` (Windows only) |

### Pygame mode (VISUALIZER = 0, default)
```bash
python wiz_drive_main.py liveTestOne.dngn
# Controls: W forward, S backward, A turn left, D turn right, Q quit
```

### Text mode (VISUALIZER = 1)
```bash
python wiz_drive_main.py liveTestOne.dngn
# Real-time keypresses (Windows-only msvcrt): W/S/A/D to move, Q to quit
```

### Text visualizer (standalone, read-only)
```bash
python text_visualizer.py liveTestOne.dngn
```

### Map loader (standalone, for inspection/debugging)
```bash
python map_loader.py liveTestOne.dngn
```

---

## Dungeon File Format (`.dngn`)

```
<Dungeon Name>
<N>              ← number of floors declared

<floor 1 block>

<floor 2 block>
...
```

Each floor block (separated from others by blank lines):
```
<S>              ← grid size; map is S×S
<row 0>          ← top row as displayed; space-separated 0/1 tokens (0=open, 1=wall)
...
<row S-1>        ← bottom row as displayed
<px> <py>        ← player start coordinates
<facing>         ← N/E/S/W or north/east/south/west (case-insensitive)
[ENEMY|name|px py]                         ← uses stats from ENEMY_TYPES library
[ENEMY|name|hp|attack|speed|px py]         ← explicit stats
[ITEM|name|px py]                          ← uses value/description/category/effect from ITEM_TYPES library
[ITEM|name|value|description|px py]        ← explicit value/description (category/effect still from library by name)
[STAIRS|px py]
```

Object descriptor lines are optional and can appear in any order after the facing line. Every x/y coordinate must be within bounds and on an open tile (`0`).

XP for explicit-stat enemies is always looked up from `ENEMY_TYPES` (xp is not part of the map format).

### Coordinate Convention

- **File order**: rows are written top-to-bottom (row 0 = top of the visual map).
- **Internal grid**: rows are reversed on load so `grid[y][x]` with `y=0` at the *bottom* (standard math orientation).
- **Directions**: north=(0,+1), south=(0,-1), east=(+1,0), west=(-1,0).
- The pygame visualizer's `_to_screen` inverts y again so north renders upward on screen.

---

## Architecture

### Data Flow

```
.dngn file
    │
    ▼
map_loader.load_map_file()
    │  returns (name, numFloors, [FloorData, ...])
    │
    ▼
FloorData = (grid, playerPos, facing, enemies, items, stairs)
    │
    ├─▶ Player object  (player.py)
    │
    ├─▶ GameState  (game_state.py)   movement / combat / floor dispatch via apply_key()
    │
    └─▶ Visualizer
           ├── MapVisualizer.draw()      (pygame)
           └── render_floor()            (text/ASCII)
```

### `FloorData` type alias (`map_loader.py`)
```python
FloorData = tuple[
    List[List[int]],          # grid[y][x]: 0=open, 1=wall
    Tuple[int, int],          # player start (x, y)
    str,                      # facing: "north"|"east"|"south"|"west"
    List[Enemy],
    List[Item],
    Tuple[int, int] | None,   # stairs position, or None
]
```

### `map_loader.py` Public API

| Function | Purpose |
|----------|---------|
| `load_map_file(path)` | Load from a `.dngn` file on disk |
| `load_map_text(text)` | Load from a string (same format) |
| `validate_map_file(path)` | Returns `(is_valid, [errors])` without loading for use |

Set `map_loader.debug = False` (as done in all entry-point files) to suppress verbose `[DEBUG]` output.

---

## Combat

When the player moves (`w`/`s`) into a tile occupied by an enemy, `GameState._do_combat()` triggers.

### Strike mechanic (`Player.strike(enemy)`)
- Hit roll: `random.random() < self.attack` (default 50% chance)
- On hit: damage = `self.strength + self.weapon.strength`. `self.weapon` is `None` until a weapon is picked up; `Item.strength` is a property returning `effect["strength"]` (0 for non-weapons), so any `Item` satisfies the weapon-slot contract.
- On miss: no damage dealt
- Either way, the enemy counter-attacks: `max(1, enemy.attack - self.defense)` damage to player
- Returns `True` on kill

## Item Pickup & Inventory

When the player moves (`w`/`s`) onto an open tile, `GameState.apply_key()` collects **every** item on that tile (after the move, before the stairs check):
- Each item is stamped with `origin_floor`, passed to `Player.pick_up(item)`, and removed from the live floor item list (so both visualizers stop drawing it — no visualizer code is involved).
- `Player.pick_up()` appends to `Player.inventory` and **auto-equips** the item when `item.category == "weapon"` and its `strength` exceeds the currently equipped weapon's.
- Combat takes precedence: moving into an enemy tile triggers `strike()` and the player does not advance, so no pickup happens there.

Persistence: `save()` writes `inventory` (each item's name/value/description/category/effect/grid_x/grid_y/origin_floor) and `equipped_weapon` (the inventory index of the equipped item, or `null`). `from_save()` rebuilds the `Item`s, restores `weapon` as the same inventory object, and removes each collected item from its `origin_floor` so it does not respawn. This bumped `SCHEMA_VERSION` to **2**; legacy v0/v1 saves load with an empty inventory.

## Floor Transitions

Also handled in `GameState.apply_key()`: stepping onto a `STAIRS` tile (after a successful move) advances `floor_index` and resets the player to the new floor's start position and facing. If no next floor exists, a message is printed.

---

## Coding Conventions

- **Python 3.11+**, no virtual-environment setup checked in; runtime external dependencies must be declared in `requirements.txt` (test-only dependencies such as `pytest` are exempt).
- **Type hints** used throughout. Use `from __future__ import annotations` for forward references.
- **Error messages** use `!r` (repr) formatting for untrusted/user-supplied values.
- **`map_loader.debug`** is a module-level bool. Set it to `False` in every entry-point file before calling any loader function. Never leave it `True` in committed code that runs as part of the game.
- `Enemy` and `Item` call `pygame.Surface(...)` in `__init__`, so `pygame.init()` **must** be called before any map is loaded.
- `FloorData` tuples are positional; always unpack with named variables: `grid, start_pos, start_facing, enemies, items, stairs = floor`.

---

## Testing

Run the full test suite with:
```bash
python -m pytest tests/ -v
```

Manual testing:
```bash
# Validate a dungeon file:
python map_loader.py DebugMapLoader.dngn

# Render a dungeon as ASCII:
python text_visualizer.py liveTestOne.dngn

# Open the pygame debug viewer (requires a display):
python test_visualizer.py liveTestOne.dngn
```

When adding new `.dngn` parser features, test both `load_map_file` and `validate_map_file` paths, and exercise `load_map_text` for in-memory cases.

---

## Next Priorities (from SECOND_ROADMAP.md)

1. Stairs/portals for level transitions *(partially implemented)*
2. Movement collision validation surfaced in all visualizers
3. Basic 3D perspective / first-person wall rendering (the core Wizardry feel)
4. Wall textures and UI overlay (HUD)
