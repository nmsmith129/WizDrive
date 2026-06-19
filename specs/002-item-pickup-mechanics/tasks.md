# Tasks: Item Pickup Mechanics

**Input**: Design documents from `specs/002-item-pickup-mechanics/`

**Prerequisites**: plan.md ✓ spec.md ✓

**Tests**: Per Constitution Principle I (Test-First, NON-NEGOTIABLE), test tasks are
REQUIRED. Tests are authored by the dedicated **[TEST-AGENT]** and confirmed to FAIL
before the **[IMPL-AGENT]** begins.

**Agent separation (Constitution Principle VI)**: ALL implementation and testing are
delegated to sub-agents — the orchestrator only plans, delegates, reviews. Test tasks go
to a dedicated **testing sub-agent**, implementation tasks to a separate **implementation
sub-agent**. Both run **Sonnet**. Setup/infra tasks are orchestrator work.

## Format: `[ID] [P?] [Story] [Agent] Description`

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Create `specs/002-item-pickup-mechanics/` artifacts (spec, plan, tasks) — orchestrator
- [x] T002 Write `tests/fixtures/legacy_save_v1.json` — a valid v1 save (`schema_version: 1`, all current fields, no `inventory`/`equipped_weapon`, `"dungeon": "DebugMapLoader.dngn"`, `"enemies": []`) — orchestrator

**Checkpoint**: Fixture committed — US3 backward-compat test can be written.

---

## Phase 2: User Story 1 — Collect items by walking onto them (Priority: P1) 🎯 MVP

**Goal**: Walking onto an item collects every item on that tile and removes it from the floor.

### Tests for User Story 1 (REQUIRED) ⚠️ — TEST-AGENT writes first, confirms FAIL

- [x] T003 [US1] [TEST-AGENT] In `tests/test_item_pickup.py`: stepping onto a tile with one item adds it to `player.inventory` and removes it from `state.items`; the tile is then empty.
- [x] T004 [US1] [TEST-AGENT] Multiple items on one tile are all collected in a single step.
- [x] T005 [US1] [TEST-AGENT] Stepping onto an empty tile leaves `player.inventory` unchanged.
- [x] T006 [US1] [TEST-AGENT] Moving into an enemy tile triggers combat, the player does not move, and no item is collected (item-and-enemy co-located).

### Implementation for User Story 1 — IMPL-AGENT

- [x] T007 [US1] [IMPL-AGENT] Add `self.inventory: list = []` to `Player.__init__` and a `Player.pick_up(item)` that appends to inventory (equip logic added in US2).
- [x] T008 [US1] [IMPL-AGENT] Add `GameState._item_at(x, y)` mirroring `_enemy_at`; in `apply_key()`'s successful-move branch, collect every item at the new location (`pick_up` + stamp `origin_floor` + `self.items.remove`) before the stairs check.

**Checkpoint**: US1 tests pass; existing suite green.

---

## Phase 3: User Story 2 — Auto-equip stronger weapons (Priority: P2)

**Goal**: Picking up a stronger weapon equips it and raises melee damage immediately.

### Tests for User Story 2 (REQUIRED) ⚠️ — TEST-AGENT writes first, confirms FAIL

- [x] T009 [P] [US2] [TEST-AGENT] `Item.strength` returns `effect["strength"]` for a weapon and `0` when absent.
- [x] T010 [US2] [TEST-AGENT] Picking up a weapon (category `weapon`, strength bonus) sets `player.weapon`; a weaker or non-weapon item does not replace a better equipped weapon.
- [x] T011 [US2] [TEST-AGENT] Under the `always_hit` fixture, `strike()` damage after equipping equals base strength + weapon strength.

### Implementation for User Story 2 — IMPL-AGENT

- [x] T012 [US2] [IMPL-AGENT] Add read-only `Item.strength` property → `self.effect.get("strength", 0)`.
- [x] T013 [US2] [IMPL-AGENT] Extend `Player.pick_up` to equip the item when `item.category == "weapon"` and `item.strength` beats the equipped weapon's; print pickup/equip messages.

**Checkpoint**: US2 tests pass; US1 + existing suite green.

---

## Phase 4: User Story 3 — Persist inventory across save/load (Priority: P3)

**Goal**: Inventory and equipped weapon survive save/reload; collected items don't respawn; legacy saves load.

### Tests for User Story 3 (REQUIRED) ⚠️ — TEST-AGENT writes first, confirms FAIL

- [x] T014 [P] [US3] [TEST-AGENT] `SCHEMA_VERSION == 2` and `save()` writes `schema_version: 2`.
- [x] T015 [US3] [TEST-AGENT] Inventory + equipped weapon round-trip through `save()` → `from_save()`.
- [x] T016 [US3] [TEST-AGENT] A collected item does not reappear on its origin floor after reload.
- [x] T017 [US3] [TEST-AGENT] Loading `tests/fixtures/legacy_save_v1.json` yields an empty inventory and `weapon is None`, with other state intact.
- [x] T018 [US3] [TEST-AGENT] A save with `schema_version: 3` is rejected with `ValueError`.

### Implementation for User Story 3 — IMPL-AGENT

- [x] T019 [US3] [IMPL-AGENT] Bump `SCHEMA_VERSION = 2`; `from item import Item`.
- [x] T020 [US3] [IMPL-AGENT] `save()`: serialize `inventory` (name, value, description, category, effect, grid_x, grid_y, origin_floor) and `equipped_weapon` (inventory index or `None`).
- [x] T021 [US3] [IMPL-AGENT] `from_save()`: rebuild inventory `Item`s, restore `player.weapon` from `equipped_weapon`, and remove each collected item from its `origin_floor`'s item list (match by grid_x, grid_y, name). Keep the newer-version guard.

**Checkpoint**: All US3 tests pass; full suite green.

---

## Phase 5: Polish & Cross-Cutting

- [x] T022 [P] Run `python -m pytest tests/ -v` — zero regressions — orchestrator
- [x] T023 [P] Update `CLAUDE.md` (combat weapon slot, item pickup flow, schema v2), `SECOND_ROADMAP.md` (pickup/inventory/weapon-equip markers), and `MEMORY.md` (design entry) — orchestrator

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: start immediately; T002 fixture needed before T017.
- **US1 (Phase 2)**: MVP; depends only on Phase 1.
- **US2 (Phase 3)**: extends `pick_up` from US1 (T013 depends on T007); T012 independent.
- **US3 (Phase 4)**: depends on US1 inventory existing; T019–T021 build on `save()`/`from_save()`.
- **Polish (Phase 5)**: after all stories.

### Agent assignment (single session)

- TEST-AGENT: T003–T006, T009–T011, T014–T018 (all test writing, confirm FAIL first).
- IMPL-AGENT: T007, T008, T012, T013, T019, T020, T021 (all implementation).
- Orchestrator: T001, T002, T022, T023.

## Notes

- `player.py` adds no `pygame` import (Principle III).
- Visualizers need no changes — they render the live `items` list.
- `STATE_FILE` monkeypatch + `SDL_VIDEODRIVER=dummy` headless patterns already exist in `tests/`.
