# Implementation Plan: Item Pickup Mechanics

**Branch**: `claude/feature-prioritization-s7mu2h` | **Date**: 2026-06-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-item-pickup-mechanics/spec.md`

## Summary

Let the player collect items by walking onto them: each item on the entered tile moves
from the floor's item list into a new `Player.inventory`, and a picked-up weapon
auto-equips when its strength bonus beats the equipped weapon's. Persist the inventory
and equipped weapon in `game_state.json`, bumping `SCHEMA_VERSION` 1 → 2, and ensure
collected items do not respawn on reload. Ship pickup, auto-equip, and persistence
regression tests.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `pygame` (runtime); `pytest` (test only — exempt from
`requirements.txt`). No new dependencies.

**Storage**: `game_state.json` — flat JSON, single slot, `STATE_FILE` in `game_state.py`.

**Testing**: pytest (`python -m pytest tests/ -v`), headless via `SDL_VIDEODRIVER=dummy`
in `tests/conftest.py`.

**Target Platform**: Windows + Linux — save/load is stdlib `json`; platform-neutral.

**Project Type**: Desktop game (dungeon crawler).

**Constraints**: No new runtime dependency; all existing saves must remain loadable;
core logic stays rendering-agnostic (`player.py` keeps no `pygame` import).

**Scale/Scope**: 3 source files touched (`player.py`, `item.py`, `game_state.py`),
no visualizer or loader changes; ~1 new test module + 1 fixture.

## Constitution Check

*GATE: Must pass before implementation. Re-checked after design.*

- [x] **I. Test-First (NON-NEGOTIABLE)**: Pickup, auto-equip, and persistence tests are
      authored by the testing sub-agent and confirmed to FAIL before implementation.
- [x] **II. Data-Driven Content**: Weapon strength comes from the item's `effect`
      (sourced from `ITEM_TYPES`), not hardcoded per item. The new `Item.strength`
      property reads `effect.get("strength", 0)`.
- [x] **III. Rendering-Agnostic Core**: Changes touch `player.py`, `item.py`,
      `game_state.py` only. `player.py` adds no `pygame` import. Visualizers render the
      live `items` list, so removed items vanish with no visualizer changes.
- [x] **IV. Consistent Code Style**: `SCHEMA_VERSION` UPPER_SNAKE_CASE, type hints,
      `!r` in any error message, single-line method comments for non-obvious logic.
- [x] **V. Backward-Compatible Persistence**: `schema_version` bumps to 2; `from_save()`
      reads `inventory`/`equipped_weapon` with `.get` defaults; a legacy fixture
      regression test asserts old saves still load (empty inventory).
- [x] **VI. Sub-Agent Execution & Test Independence**: Testing and implementation go to
      separate Sonnet sub-agents. No Opus escalation needed.
- [x] **Constraints**: No new runtime dependency; stdlib `json`; platform-neutral.

All gates **PASS**. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/002-item-pickup-mechanics/
├── plan.md          ← this file
├── spec.md          ← feature spec
└── tasks.md         ← task breakdown (TEST-AGENT / IMPL-AGENT)
```

### Source Code Changes

```
player.py        ← add inventory list + pick_up()
item.py          ← add strength read-only property
game_state.py    ← _item_at(); pickup in apply_key(); SCHEMA_VERSION=2; inventory in save()/from_save(); import Item
tests/
├── fixtures/
│   └── legacy_save_v1.json   ← new: v1 save with no inventory field
└── test_item_pickup.py       ← new: pickup + auto-equip + persistence tests
```

No new top-level modules. No changes to `map_visualizer.py`, `text_visualizer.py`,
`map_loader.py`.

## Implementation Approach

### `player.py` — implementation sub-agent
- Add `self.inventory: list = []` in `__init__`.
- Add `pick_up(item)`: append to `inventory`; if `item.category == "weapon"` and
  `item.strength > (self.weapon.strength if self.weapon else 0)`, set `self.weapon = item`.
  Print a pickup line, plus an equip line when equipped (matches the `print(...)` combat
  feedback style).

### `item.py` — implementation sub-agent
- Add a read-only `strength` property returning `self.effect.get("strength", 0)`, so an
  `Item` satisfies the weapon-slot contract `strike()` already relies on
  (`self.weapon.strength`). No change to `strike()` or the combat test's
  `SimpleNamespace(strength=4)` stub.

### `game_state.py` — implementation sub-agent
- Add `_item_at(x, y)` mirroring `_enemy_at(x, y)`.
- In `apply_key()`'s successful-move `else` branch, after `self.player.move(...)` and
  before the stairs check: while an item is at the player's location, `pick_up` it,
  stamp `item.origin_floor = self.floor_index`, and `self.items.remove(item)`.
- `SCHEMA_VERSION = 2`; `from item import Item`.
- `save()`: add `"inventory"` (per item: name, value, description, category, effect,
  grid_x, grid_y, origin_floor) and `"equipped_weapon"` (inventory index or `None`).
- `from_save()`: keep the `save_version > SCHEMA_VERSION` guard; rebuild `Item`s from
  `data.get("inventory", [])` into `player.inventory`; restore `player.weapon` from
  `data.get("equipped_weapon")`; for each collected item, remove the matching item
  (by `grid_x, grid_y, name`) from its `origin_floor`'s re-parsed item list so it does
  not respawn.

### `tests/` — testing sub-agent
New `tests/test_item_pickup.py` plus `tests/fixtures/legacy_save_v1.json`. See tasks.md
for the per-test breakdown. Reuse `conftest.py` headless init, the `always_hit` fixture
from `test_combat.py`, and `STATE_FILE` monkeypatching from `test_state.py`.

## Complexity Tracking

> No Constitution violations — section intentionally empty.
