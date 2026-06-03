# WizDrive — CLAUDE.md

WizDrive is a Python/Pygame dungeon crawler inspired by Wizardry. The project is in active early development: the core map system, entity classes, and multiple visualizer backends are complete; first-person 3D rendering and most gameplay mechanics are still on the roadmap.

---

## Repository Layout

```
wiz_drive_main.py          Entry point; selects visualizer mode, runs the game loop
map_loader.py             .dngn file parser, validator, and loader
player.py                Player class (position, facing, movement, stubs for combat/spells)
enemy.py                 Enemy class (extends pygame.sprite.Sprite) + ENEMY_TYPES table + get_stats()
item.py                  Item class — extends pygame.sprite.Sprite
map_visualizer.py         Pygame top-down 2D map renderer + standalone debug viewer
text_visualizer.py        ASCII terminal renderer, renders current floor as text
game_state.py            GameState: runtime state, movement/combat dispatch, JSON save/load
test_visualizer.py       Manual test script for the pygame debug viewer
DebugMapLoader.dngn      Minimal two-floor dungeon used for parser debugging
liveTestOne.dngn         Richer two-floor dungeon with stairs, enemies, items
game_state.json          (git-ignored) Runtime save file written by GameState.save()
ROADMAP.md               Full feature roadmap (8 phases)
ROADMAP_PRIORITY.md      Same features ordered by implementation sequence
SECOND_ROADMAP.md        Dependency-ordered roadmap
```

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
[ITEM|name|value|description|px py]
[STAIRS|px py]
```

Object descriptor lines are optional and can appear in any order after the facing line. Every x/y coordinate must be within bounds and on an open tile (`0`).

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

### Key Classes

**`Player`** (`player.py`) — no pygame dependency  
`location: (x, y)`, `facing: str`  
Attributes (defaults): `attack: float = 0.5` (hit chance), `strength: int = 1` (base damage), `defense: int = 1` (damage reduction), `max_hp: int = 10`, `intelligence: int = 1` (spell effectiveness, unused until spells exist), `mana: int = 1` (max mana). `weapon = None` is an equipment stub exposing `.strength` once filled.  
`hp`/`mp` are the *current* HP/mana; they start full (`max_hp`/`mana`) unless passed explicitly.  
`move("forward"|"backward")`, `turn("left"|"right")`, `strike(enemy)`  
`cast_spell()`, `use_item()` are placeholder stubs.

**`Enemy`** (`enemy.py`) — extends `pygame.sprite.Sprite`  
Rendered as a red 32×32 surface. Fields: `name`, `hp`, `attack`, `speed`, `grid_x`, `grid_y`.  
Stats for named enemies come from `enemy.ENEMY_TYPES`; unknown names fall back to `{hp:10, attack:3, speed:1}`.

**`Item`** (`item.py`) — extends `pygame.sprite.Sprite`  
Rendered as a gold/yellow 32×32 surface. Fields: `name`, `value`, `description`, `grid_x`, `grid_y`.

### `map_loader.py` Public API

| Function | Purpose |
|----------|---------|
| `load_map_file(path)` | Load from a `.dngn` file on disk |
| `load_map_text(text)` | Load from a string (same format) |
| `validate_map_file(path)` | Returns `(is_valid, [errors])` without loading for use |

Set `map_loader.debug = False` (as done in all entry-point files) to suppress verbose `[DEBUG]` output.

---

## Combat

Combat is dispatched by `GameState.apply_key()` (`game_state.py`): when the player moves (`w`/`s`) into a tile occupied by an enemy, `Player.strike(enemy)` (`player.py`) runs instead of movement:

- `strike()` rolls `random.random() < player.attack` to hit. On a hit the player deals `strength + weapon.strength` damage (weapon strength is 0 while `weapon is None`).
- On a kill: the enemy is removed from the enemy list, its `xp` is awarded to the player, and the player levels up once per 10 XP.
- Whether the strike missed or the enemy merely survived, the enemy counter-attacks for `max(1, enemy.attack - player.defense)` (always at least 1).

`Player.strike()` returns `True` when the enemy is defeated. Player death is printed but does not halt the game loop yet. Combat is now probabilistic, so tests monkeypatch `player.random.random` for determinism.

## Floor Transitions

Also handled in `GameState.apply_key()`: stepping onto a `STAIRS` tile (after a successful move) advances `floor_index` and resets the player to the new floor's start position and facing. If no next floor exists, a message is printed.

---

## Coding Conventions

- **Python 3.11+**, no virtual-environment setup checked in; `pygame` is the only external dependency.
- **Type hints** used throughout. Use `from __future__ import annotations` for forward references.
- **Naming**: `snake_case` for modules, functions, and variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants. `_leading_underscore` for module-private functions.
- **Error messages** use `!r` (repr) formatting for untrusted/user-supplied values.
- **No comments** on obvious code. Comments appear only for non-obvious constraints (e.g. "pygame must be initialized before load_map_file").
- **`map_loader.debug`** is a module-level bool. Set it to `False` in every entry-point file before calling any loader function. Never leave it `True` in committed code that runs as part of the game.
- `Enemy` and `Item` call `pygame.Surface(...)` in `__init__`, so `pygame.init()` **must** be called before any map is loaded.
- `FloorData` tuples are positional; always unpack with named variables: `grid, start_pos, start_facing, enemies, items, stairs = floor`.

---

## Development Branch

All feature work goes on branch **`claude/claude-md-docs-wwQy2`**. Push with:
```bash
git push -u origin claude/claude-md-docs-wwQy2
```

---

## Next Priorities (from SECOND_ROADMAP.md)

1. Multiple enemy types (distinct visuals/behaviour)
2. Stairs/portals for level transitions *(partially implemented in GameState.apply_key)*
3. Movement collision validation surfaced in all visualizers
4. Basic 3D perspective / first-person wall rendering (the core Wizardry feel)
5. Wall textures and UI overlay (HUD)

---

## Testing

The project has a `pytest` suite under `tests/`. Run it with:

```bash
python -m pytest -q
```

`tests/conftest.py` sets the dummy SDL video/audio drivers automatically, so the
suite runs headless (no display needed) even though `enemy.py`/`item.py` create
pygame Surfaces. Current coverage by file:

| Test file | Covers |
|-----------|--------|
| `test_map_loader.py` | `load_map_file` / `load_map_text`, grid reversal, enemy/item/stairs/player parsing, multi-floor |
| `test_validate_map.py` | `validate_map_file` valid + error paths |
| `test_player.py` | `Player` init, attribute defaults, movement, turning |
| `test_combat.py` | `Player.strike` (hit/miss rolls, weapon damage, counter-attacks), wall detection |
| `test_state.py` | `GameState` save/load round-trip |
| `test_enemy_types.py` | `ENEMY_TYPES` / `get_stats` |
| `test_text_visualizer.py` | ASCII rendering, symbol priority, facing line |

When adding new `.dngn` parser features, test both `load_map_file` and `validate_map_file` paths, and exercise `load_map_text` for in-memory cases.

### Manual checks

```bash
# Validate a dungeon file:
python map_loader.py DebugMapLoader.dngn

# Render a dungeon as ASCII:
python text_visualizer.py liveTestOne.dngn

# Open the pygame debug viewer (requires a display):
python test_visualizer.py liveTestOne.dngn
```
