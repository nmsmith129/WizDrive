<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-persistence-schema-versioning/plan.md
<!-- SPECKIT END -->

# WizDrive — CLAUDE.md

> **Project memory** is kept in [`MEMORY.md`](MEMORY.md) at the repo root (shared on the network drive). Read it at the start of a session and record any cross-session context there — not in this file. This file is hand-maintained project documentation only.

WizDrive is a **traditional ASCII roguelike** in the lineage of the 1980s classics (Rogue, NetHack, Angband) and modern-classic **Brogue** — turn-based, grid-based, procedurally generated. It is built in **Godot 4.7 / GDScript** and targets **Android, Linux, and Windows 11**.

The project is an early, clean-slate rebuild: the architecture is deliberately open and being worked out as it goes, so the codebase is currently a small set of foundational utilities. This file documents only what actually exists today and grows as the code does. (An earlier Python/Pygame incarnation is archived under [`archive/`](archive/) for reference only — it is not a translation target.)

---

## Working Style

The developer is learning GDScript and drives the implementation: he types the code himself while Claude guides — explaining concepts, naming the relevant APIs, and pointing at the specific error or line. Don't write or edit GDScript files during a learning exercise or when he's driving; running/verifying headless and reading files to review is fine. Treat project setup and scaffolding as his to do unless he asks otherwise.

---

## Project Layout

| Path | Contents |
|------|----------|
| [`scripts/`](scripts/) | Game code (GDScript) |
| [`scripts/resources/`](scripts/resources/) | `Resource`-derived data classes |
| [`tests/`](tests/) | Home-grown headless test suite |
| [`project.godot`](project.godot) | Godot project config — Compatibility (`gl_compatibility`) renderer, chosen with the Android target in mind |
| [`archive/`](archive/) | Retired Python/Pygame source (reference only) |
| `docs/`, `specs/`, `.specify/` | Design docs and Spec Kit artifacts, kept at the repo root |

---

## What Exists Today

| File | Class | Purpose |
|------|-------|---------|
| [`scripts/resources/game_constants.gd`](scripts/resources/game_constants.gd) | `GameConstants` | `FOURWAY` / `EIGHTWAY` `Array[Vector2i]` direction tables |
| [`scripts/pathfinding.gd`](scripts/pathfinding.gd) | `Pathfinding` | Static Dijkstra utilities: `dijkstra_map_4` and `dijkstra_map_8` |
| [`scripts/resources/floor_data.gd`](scripts/resources/floor_data.gd) | `FloorData` | One floor's grid; `size()`, `is_wall(x, y)`, `wall_tiles()` |

### `Pathfinding`
Both functions take a fully decoupled `(start: Vector2i, blocked: Array[Vector2i], size: int)` signature and return a **Dijkstra distance map** `Dictionary[Vector2i, int]` — a distance field, *not* a path. Derive a path (or monster movement) by rolling downhill from any tile toward `start`. This is the classic **Brogue "Dijkstra map"** technique for AI, pursuit, and autoexplore. (Uniform-cost BFS under the hood; the 8-way variant currently allows corner-cutting.)

### `FloorData` (`extends Resource`)
Deliberately lean: `@export var grid: Array[PackedInt32Array]` (0 = open, 1 = wall). `is_wall(x, y)` is bounds-safe (off-map reads as wall). The intent is for walls to live in a dynamically-updated blocked-list on the future game-state controller, with `FloorData` a seldom-read source of truth.

---

## Grid & Coordinate Convention

- Grid is indexed `grid[y][x]` with **`y = 0` at the bottom** (standard math orientation).
- Directions: **north = +y, south = −y, east = +x, west = −x**. See `GameConstants.FOURWAY` / `EIGHTWAY`.

---

## Running Tests

The suite is a DIY runner (no GUT/GdUnit4 yet): plain `RefCounted` test classes with `run(t)` share a `TestContext` (`check()` + pass/fail counters), all driven by one `SceneTree` script, [`tests/test_main.gd`](tests/test_main.gd), which aggregates to a single summary and exit code.

```powershell
godot_console --headless --path . --script res://tests/test_main.gd
```

**Use `godot_console.exe`, not `godot.exe`.** The plain `godot` on PATH is the GUI build; run headless from PowerShell it detaches from the console, so the run appears to hang and no exit code comes back. `godot_console.exe` (a thin console launcher next to it in `C:\Godot`) blocks until done, streams stdout, and returns a real exit code — which the suite's `quit(1 if failed else 0)` gating depends on.

---

## Coding Conventions

- **Static typing throughout**: annotate variables, parameters, and return types (`func size() -> int:`, `var walls: Array[Vector2i] = []`).
- **Naming**: `snake_case` for functions and variables, `PascalCase` for `class_name`, `UPPER_SNAKE_CASE` for constants.
- **Comments**: `##` doc comments for a class or member; `#` for inline notes inside a body. Comment on intent, not the obvious.
- Data classes derive from `Resource`; stateless helpers are `static func`s on a `RefCounted` class.

---

## Next

Map generation — a generator that outputs a `FloorData`, using `dijkstra_map_4` as the connectivity check (flood from the entrance, reject layouts with unreachable open tiles). Open design question to settle first: **procedural vs. hand-authored** maps (a traditional roguelike leans procedural).
