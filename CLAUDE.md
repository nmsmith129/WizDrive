<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# WizDrive — CLAUDE.md

> **Memory instruction:** This project lives on a remote server shared across multiple clients. Do not write project memories to the local `~/.claude/` memory store. Instead, update this file directly with any new context worth preserving across sessions.
>
> Additionally, at the start of your first response in any new session, check whether your local project memory for this project contains a `feedback-memory-location.md` file. If it does not exist, create it with the following content:
>
> ```
> ---
> name: feedback-memory-location
> description: New memories for WizDrive must go into CLAUDE.md, not local storage
> metadata:
>   type: feedback
> ---
>
> For this project, write all new persistent context directly into `CLAUDE.md` at the project root — do not use the local `~/.claude/projects/` memory store.
>
> **Why:** The project lives on a remote server shared across multiple client machines. Local memory is machine-specific. CLAUDE.md is on the remote share and is loaded automatically by Claude Code everywhere.
>
> **How to apply:** Any time you would normally write a memory file, edit CLAUDE.md instead.
> ```
>
> Also add a pointer in the same directory's `MEMORY.md`: `- [Memory Location](feedback-memory-location.md) — New memories go into CLAUDE.md, not local storage`

WizDrive is a Python/Pygame dungeon crawler inspired by Wizardry. The project is in active early development: the core map system, entity classes, combat, XP/leveling, and player attribute systems are complete; first-person 3D rendering and most gameplay mechanics are still on the roadmap.

---

## Repository Layout

```
wiz_drive_main.py        Entry point; selects visualizer mode, runs the game loop
game_state.py            GameState class: all runtime state, combat logic, save/load
map_loader.py            .dngn file parser, validator, and loader
player.py                Player class (position, facing, movement, attributes, XP/level)
enemy.py                 Enemy class (extends pygame.sprite.Sprite) + ENEMY_TYPES table & get_stats() helper
item.py                  Item class (extends pygame.sprite.Sprite) + ITEM_TYPES table & get_item_stats() helper
map_visualizer.py        Pygame top-down 2D map renderer + standalone debug viewer
text_visualizer.py       ASCII terminal renderer, renders current floor as text
test_visualizer.py       Manual test script for the pygame debug viewer
tests/                   Automated test suite (pytest, 149 tests)
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

### Key Classes

**`Player`** (`player.py`) — no pygame dependency  
`location: (x, y)`, `facing: str`, `hp: int`, `mp: int`, `xp: int`, `level: int`  
Attributes: `attack: float`, `strength: int`, `defense: int`, `max_hp: int`, `intelligence: int`, `mana: int`  
`move("forward"|"backward")`, `turn("left"|"right")`, `strike(enemy)`  
`cast_spell()`, `use_item()` are placeholder stubs.  
`self.weapon = None` is an equipment stub; any object with `.strength` works once equipment exists.

**`Enemy`** (`enemy.py`) — extends `pygame.sprite.Sprite`  
Rendered as a red 32×32 surface. Fields: `name`, `hp`, `attack`, `speed`, `grid_x`, `grid_y`, `xp`.  
Stats for named enemies come from `enemy.ENEMY_TYPES`; unknown names fall back to `{hp:10, attack:3, speed:1, xp:0}`.

**`Item`** (`item.py`) — extends `pygame.sprite.Sprite`  
Rendered as a gold/yellow 32×32 surface. Fields: `name`, `value`, `description`, `category` (`weapon`/`armor`/`consumable`/`treasure`/`misc`), `effect` (category-specific bonus dict, e.g. `{"strength": 4}`), `grid_x`, `grid_y`.  
Named items can pull `value`/`description`/`category`/`effect` from `item.ITEM_TYPES` via `get_item_stats()`; unknown names fall back to `{value:1, category:"misc", description:""}`.

**`GameState`** (`game_state.py`)  
All runtime state: current floor, player, enemies, items. Handles combat logic, floor transitions, save/load to `game_state.json`.

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
- On hit: damage = `self.strength + self.weapon.strength` (weapon is `None` stub, treated as 0)
- On miss: no damage dealt
- Either way, the enemy counter-attacks: `max(1, enemy.attack - self.defense)` damage to player
- Returns `True` on kill

### XP & Leveling
- On kill: player earns `enemy.xp` XP. Every 10 XP = 1 level.
- Level-up logic: `levels_gained = (xp_after // 10) - (xp_before // 10)` — handles multi-level jumps.
- `enemy.xp` is an instance attribute set at construction from `ENEMY_TYPES`; it is not re-looked up at combat time.

### XP values by enemy type
| Enemy | XP | Enemy | XP |
|-------|----|-------|----|
| Rat | 5 | Troll | 30 |
| Spider | 10 | Dark Mage | 35 |
| Goblin | 15 | Orc | 40 |
| Skeleton | 20 | Wraith | 45 |
| Zombie | 25 | Vampire | 50 |
| | | Dragon | 100 |

`Player.strike()` returns `True` when the enemy is defeated. Player death is printed but does not halt the game loop yet. Combat is now probabilistic, so tests monkeypatch `player.random.random` for determinism.

---

## Player Attribute System

Six custom attributes on `Player` (not D&D stats):

| Field | Default | Role |
|-------|---------|------|
| `attack` | `0.5` | hit chance (`random.random() < self.attack`) |
| `strength` | `1` | base damage per hit |
| `defense` | `1` | damage reduction (`max(1, enemy.attack - defense)`) |
| `max_hp` | `10` | maximum HP; `self.hp` starts full |
| `intelligence` | `1` | spell effectiveness (stub — spells not yet implemented) |
| `mana` | `1` | maximum mana; `self.mp` starts full |

`Player.__init__` signature: `Player(name, hp=None, mp=None, attack=0.5, strength=1, defense=1, max_hp=10, intelligence=1, mana=1)`. `hp`/`mp` default to `max_hp`/`mana` when omitted.

Enemies deliberately have no attributes — they keep their `ENEMY_TYPES` stat block (`hp`, `attack`, `speed`). Enemy miss chance is planned but not yet implemented.

---

## Persistence (`game_state.py`)

`GameState.save()` writes all player fields to `game_state.json`, including `xp`, `level`, and all six attributes.  
`GameState.from_save()` restores each with `.get(field, default)` fallbacks so pre-attribute and pre-XP saves still load correctly.

---

## Floor Transitions

Also handled in `GameState.apply_key()`: stepping onto a `STAIRS` tile (after a successful move) advances `floor_index` and resets the player to the new floor's start position and facing. If no next floor exists, a message is printed.

---

## Coding Conventions

- **Python 3.11+**, no virtual-environment setup checked in; `pygame` is the only external dependency.
- **Type hints** used throughout. Use `from __future__ import annotations` for forward references.
- **Naming**: `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants, `_leading_underscore` for module-private functions. The module *file* stays `snake_case` even when it contains a `PascalCase` class (e.g. `map_visualizer.py` → `class MapVisualizer`).
- **Comments**: single-line `# comment` as the first line of a method body for non-obvious logic. Not docstrings. No comments on obvious code.
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

149 tests across: `test_combat`, `test_enemy_types`, `test_item_types`, `test_map_loader`, `test_player`, `test_state`, `test_text_visualizer`, `test_validate_map`.

Tests import from `game_state` and `player` directly.  
Combat tests (`test_combat.py`) monkeypatch `player.random.random` via `always_hit`/`always_miss` fixtures for determinism.

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

1. Multiple enemy types (distinct visuals/behaviour)
2. Stairs/portals for level transitions *(partially implemented)*
3. Movement collision validation surfaced in all visualizers
4. Basic 3D perspective / first-person wall rendering (the core Wizardry feel)
5. Wall textures and UI overlay (HUD)
