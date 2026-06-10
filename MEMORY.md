# WizDrive — Project Memory

This file holds persistent, cross-session context (memories) for the WizDrive
project. It lives on the network share, so it is visible from every machine that
opens `\\grimoire.local\share\WizDrive` and is version-controlled with the repo.

**Convention:**
- This whole file is "memory." `CLAUDE.md` is hand-maintained project
  documentation; this file is where Claude records things worth remembering
  across sessions.
- Entries inside the `MEMORIES` managed block below are added/updated by Claude.
  Anything you want to hand-write, put it *outside* that block.
- Each entry: a `### slug` heading, a one-line summary, then the detail. For
  feedback/decisions, include **Why** and **How to apply**. Use absolute dates.
- **Dual-write:** every entry here is also mirrored as a normal memory file in the
  per-machine local store (`~/.claude/projects/.../memory/`). This shared
  `MEMORY.md` is the **source of truth** — if a local mirror ever disagrees, this
  file wins.

<!-- MEMORIES START -->

### memory-location-decision
Persistent memory is dual-written to BOTH this share-root `MEMORY.md` and the per-machine `~/.claude` local store; `CLAUDE.md` is hand-maintained docs only and never holds memories.
**Why:** On 2026-06-08 the user removed the old "write memories into CLAUDE.md" instruction. They chose a shared file so memory is visible across every client machine that opens the network share (the local `~/.claude` store is per-machine), and additionally asked that memories also be kept in the normal local files. On any disagreement between the two copies, this `MEMORY.md` is authoritative.
**How to apply:** Record new cross-session context as an entry in this file's MEMORIES block AND as a normal memory file (+ index pointer) in the local store. Never append memories to `CLAUDE.md`.

### project-wizdrive-overview
Core architecture and file layout of the WizDrive dungeon crawler. (type: project)
**Why:** Personal game project under active development.
**How to apply:** Use as orientation when touching any part of the codebase.

WizDrive is a Python dungeon crawler with a pygame renderer and a text/terminal visualizer mode.

Key files:
- `player.py` — `Player` class: name, hp, mp, xp, level, location, facing, plus six attributes
- `enemy.py` — `Enemy(pygame.sprite.Sprite)`: name, hp, attack, speed, grid_x, grid_y, xp. Also holds the `ENEMY_TYPES` dict + `get_stats(name)` returning an `EnemyStats` TypedDict (hp, attack, speed, xp)
- `item.py` — `Item(pygame.sprite.Sprite)`: name, value, description, category, effect, grid_x, grid_y; `ITEM_TYPES` + `get_item_stats()`
- `game_state.py` — `GameState` class: all runtime state, combat logic, save/load to `game_state.json`
- `map_loader.py` — parses `.dngn` map files
- `text_visualizer.py` — ASCII floor renderer (`render_floor`)
- `map_visualizer.py` — pygame top-down renderer (`class MapVisualizer`)
- `wiz_drive_main.py` — entry point; `VISUALIZER` constant selects the mode: `0` = pygame top-down (default), `1` = text/terminal

Test suite:
- Located in `tests/`, run with `python -m pytest tests/ -v`
- 149 tests across: test_combat, test_enemy_types, test_item_types, test_map_loader, test_player, test_state, test_text_visualizer, test_validate_map
- Tests import from `game_state` and `player` directly

Map format:
- `.dngn` files; enemy lines: `ENEMY|name|x y` (library stats) or `ENEMY|name|hp|attack|speed|x y` (explicit)
- XP for explicit-stat enemies is always looked up from `ENEMY_TYPES` (not part of the map format)

### project-xp-level-system
XP and leveling system — design decisions and where things live. (type: project)
**Why:** Player progression feature requested by the user (implemented 2026-06-01).
**How to apply:** When touching combat, player stats, or save/load, be aware of this system.

Design:
- `Player.xp` (int, default 0) — total XP earned; in `player.py`
- `Player.level` (int, default 1) — current level; in `player.py`
- `Enemy.xp` (int) — XP reward for killing this enemy; set at construction from `ENEMY_TYPES`
- `EnemyStats` TypedDict (in `enemy.py`) includes an `xp` field; `get_stats()` default returns `xp: 0`

XP values by enemy type:
Rat:5, Spider:10, Goblin:15, Skeleton:20, Zombie:25, Troll:30, Dark Mage:35, Orc:40, Wraith:45, Vampire:50, Dragon:100

Level-up logic (in `game_state.py` `GameState._do_combat`): every 10 XP = 1 level. On kill: capture `xp_before`, add `enemy.xp`, compute `(new // 10) - (old // 10)` for levels gained. Handles multi-level jumps from a single kill.

Persistence: `save()` writes `xp` and `level` to `game_state.json`; `from_save()` restores both with `.get()` fallbacks (`xp→0`, `level→1`) for old save files.

Enemy XP source: `map_loader` always reads xp from `get_stats(name)["xp"]`, even for 6-field explicit-stat enemies (xp is not part of the map format).

### project-attribute-system
Player six-attribute system (attack/strength/defense/max_hp/intelligence/mana) — design, combat wiring, persistence. (type: project)
**Why:** User wanted Wizardry-style player stats wired into the only live mechanic (combat), fulfilling SECOND_ROADMAP.md's "Attribute system" item (implemented 2026-06-03). The classic six D&D stats were discarded for six custom player-only attributes. Enemies deliberately get no attributes — they keep their `ENEMY_TYPES` stat block.
**How to apply:** When touching combat, player init, or save/load, account for these.

Attributes (all on `Player`, `player.py`):
| Field | Default | Role |
|-------|---------|------|
| `attack` | `0.5` | hit chance (`random.random() < self.attack`) |
| `strength` | `1` | base damage = `strength + weapon.strength` |
| `defense` | `1` | damage taken = `max(1, enemy.attack - defense)` |
| `max_hp` | `10` | max HP; `self.hp` is current, starts full |
| `intelligence` | `1` | spell effectiveness (stored only; spells are stubs) |
| `mana` | `1` | max mana; `self.mp` is current, starts full |

- `Player.__init__(name, hp=None, mp=None, attack=0.5, strength=1, defense=1, max_hp=10, intelligence=1, mana=1)`. `hp`/`mp` default to `max_hp`/`mana` (start full) when omitted.
- `self.weapon = None` is an equipment stub; any object with `.strength` works once equipment exists.

Combat method rename: the old `Player.attack()` method was renamed **`strike(enemy)`** because the `self.attack` stat would have shadowed it. Caller updated in `game_state.py` `apply_key`. Combat is probabilistic: on hit deal `strength + weapon`; on miss deal nothing; **either way the enemy counter-attacks** (enemy miss chance planned later). `strike()` returns `True` on a kill.

Persistence: `game_state.py` `save()` writes all six attributes; `from_save()` restores each with `.get(field, default)` fallbacks (attack→0.5, strength/defense/intelligence/mana→1, max_hp→10) so pre-attribute saves still load. Same pattern as [[project-xp-level-system]].

Tests: combat is RNG-driven, so `tests/test_combat.py` monkeypatches `player.random.random` via `always_hit`/`always_miss` fixtures for determinism. The `PLAYER_ATTACK` constant was removed. `GameState.new` creates `Player("Hero")` (HP 10).

### feedback-coding-style
Coding conventions and style preferences confirmed in this project. (type: feedback)

Use single-line `# comment` style inside method bodies — not docstrings. This matches the existing pattern in `map_loader.py` and was applied consistently across files.
**Why:** The codebase uses inline comments, not docstrings. The user asked to "comment all uncommented methods" and accepted this style.
**How to apply:** When adding comments to methods, write `# one line` as the first line of the body, not `"""docstring"""`.

XP on `Enemy` is an instance attribute, not looked up from `ENEMY_TYPES` at combat time.
**Why:** User explicitly redirected this — "that's where xp rewards should be tracked before being awarded to the player."
**How to apply:** Enemy XP belongs on the `Enemy` object. Do not look it up from `ENEMY_TYPES` inside `_do_combat`.

Naming follows PEP 8: `snake_case` for modules/functions/variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants; `_leading_underscore` for module-private functions.
**Why:** User asked to fix class names to PascalCase after an over-zealous snake_case conversion had lowercased a class.
**How to apply:** Class names are always `PascalCase` even though everything else is snake_case. The module *file* name stays snake_case (e.g. `map_visualizer.py` contains `class MapVisualizer`).

### feedback-sub-agent-delegation
During `/speckit-implement`, delegate ALL coding and test-writing to sub-agents — the orchestrator never writes feature code or tests directly. (type: feedback)
**Why:** Constitution Principle VI is explicit on this. Violated on the 001-persistence-schema-versioning feature — wrote all code inline as the orchestrator instead of spawning a testing sub-agent and a separate implementation sub-agent.
**How to apply:** When tasks.md has `[TEST-AGENT]` tasks, spawn a Sonnet sub-agent (Agent tool) to write those tests and confirm they FAIL before implementation. Then spawn a separate Sonnet sub-agent for `[IMPL-AGENT]` tasks. Infra/setup tasks (fixture files, directory creation) are orchestrator work and don't require delegation. Opus escalation requires explicit prior user permission recorded in plan.md Complexity Tracking.

<!-- MEMORIES END -->
