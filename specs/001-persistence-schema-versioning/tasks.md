# Tasks: Persistence Schema Versioning

**Input**: Design documents from `specs/001-persistence-schema-versioning/`

**Prerequisites**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ quickstart.md ✓

**Tests**: Per WizDrive Constitution Principle I (Test-First, NON-NEGOTIABLE), test tasks
are REQUIRED for new behaviour. Tests are authored by the dedicated **[TEST-AGENT]**
and must be confirmed to FAIL before the **[IMPL-AGENT]** begins implementation.

**Agent separation (Constitution Principle VI)**: ALL implementation and testing MUST be
delegated to sub-agents — the orchestrator only plans, delegates, and reviews. Test tasks
go to a dedicated **testing sub-agent**, implementation tasks to a separate
**implementation sub-agent**. Every sub-agent runs **Sonnet by default** — Opus only
with explicit prior user permission recorded in plan.md Complexity Tracking.

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] [Agent] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- **[Agent]**: `[TEST-AGENT]` or `[IMPL-AGENT]`; setup/infra tasks omit this tag

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the test fixture directory and the v0 legacy save fixture that US1
and US3 tests depend on. No source-code changes.

- [X] T001 Create `tests/fixtures/` directory at repo root
- [X] T002 [P] Write `tests/fixtures/legacy_save_v0.json` — valid v0 save: all 19 current fields, no `schema_version` key, `"dungeon": "DebugMapLoader.dngn"`, `"enemies": []`; use schema from `specs/001-persistence-schema-versioning/data-model.md`

**Checkpoint**: Fixture file committed — US1 tests can now be written.

---

## Phase 2: Foundational (Blocking Prerequisites)

No blocking prerequisites beyond Phase 1. User story work can begin after T001–T002.

---

## Phase 3: User Story 1 — Saved games survive game updates (Priority: P1) 🎯 MVP

**Goal**: Prove that a save produced before schema versioning loads correctly after the
feature is added. Establishes the regression guard (FR-007).

**Independent Test**: Load `tests/fixtures/legacy_save_v0.json` via `GameState.from_save()`
(with `STATE_FILE` monkeypatched to the fixture path) and assert all character fields
restore to expected values.

### Tests for User Story 1 (REQUIRED — Constitution Principle I) ⚠️

> **TEST-AGENT writes these first and confirms they FAIL before implementation**
> Note: T003 will PASS against the current code (legacy loads already work) — the
> purpose is to lock in the regression guard, not to drive new code.

- [X] T003 [US1] [TEST-AGENT] Write `test_legacy_v0_save_loads` in `tests/test_schema_version.py` — monkeypatch `game_state.STATE_FILE` to `tests/fixtures/legacy_save_v0.json`, call `GameState.from_save()`, assert `player.location == (1, 1)`, `player.facing == "north"`, `player.hp == 10`, `player.mp == 1`, `player.xp == 0`, `player.level == 1`, all six attributes at defaults

### Implementation for User Story 1

- [X] T004 [US1] [IMPL-AGENT] In `game_state.py` `from_save()`, immediately after `data = json.load(f)` add: `save_version = data.get("schema_version", 0)` — establishes the version read used by US3; no behaviour change for v0 saves

**Checkpoint**: US1 test passes; existing 18 tests in `tests/test_state.py` still pass.

---

## Phase 4: User Story 2 — Save files identify their format (Priority: P2)

**Goal**: Every save written by the current game carries an integer `schema_version` field
so future load logic can make correct decisions.

**Independent Test**: Call `GameState.save()`, read the written JSON, assert
`"schema_version"` key is present with value `1`.

### Tests for User Story 2 (REQUIRED — Constitution Principle I) ⚠️

> **TEST-AGENT writes these first and confirms they FAIL (save() does not yet write schema_version)**

- [X] T005 [P] [US2] [TEST-AGENT] Write `test_save_includes_schema_version` in `tests/test_schema_version.py` — call `GameState.save()` (with `STATE_FILE` monkeypatched to a tmp path), read the JSON, assert `"schema_version" in data`
- [X] T006 [P] [US2] [TEST-AGENT] Write `test_save_schema_version_is_1` in `tests/test_schema_version.py` — same setup, assert `data["schema_version"] == 1`

### Implementation for User Story 2

- [X] T007 [US2] [IMPL-AGENT] Add module-level constant to `game_state.py` below existing imports: `SCHEMA_VERSION: int = 1`
- [X] T008 [US2] [IMPL-AGENT] In `game_state.py` `save()`, add `"schema_version": SCHEMA_VERSION` as the first key in the dict written to `STATE_FILE` (depends on T007)

**Checkpoint**: T005 and T006 pass; US1 checkpoint still holds; all existing tests pass.

---

## Phase 5: User Story 3 — Clear handling of newer/unreadable saves (Priority: P3)

**Goal**: When a save's `schema_version` exceeds `SCHEMA_VERSION`, `from_save()` raises
`ValueError` with a human-readable message instead of loading partial or incorrect state.

**Independent Test**: Write a save dict with `schema_version=2` to a tmp file, monkeypatch
`STATE_FILE`, call `GameState.from_save()`, assert `pytest.raises(ValueError)` with
message containing version numbers.

### Tests for User Story 3 (REQUIRED — Constitution Principle I) ⚠️

> **TEST-AGENT writes this first and confirms it FAILS (no rejection logic yet)**

- [X] T009 [US3] [TEST-AGENT] Write `test_newer_version_save_raises` in `tests/test_schema_version.py` — write `{"schema_version": 2, "dungeon": "DebugMapLoader.dngn", ...minimal fields...}` to tmp file, monkeypatch `STATE_FILE`, call `GameState.from_save()`, use `pytest.raises(ValueError)` and assert version numbers appear in the message

### Implementation for User Story 3

- [X] T010 [US3] [IMPL-AGENT] In `game_state.py` `from_save()`, immediately after T004's `save_version = data.get("schema_version", 0)` line, add: `if save_version > SCHEMA_VERSION: raise ValueError(f"Save is from a newer version of WizDrive (save {save_version!r} > supported {SCHEMA_VERSION!r}).")` (depends on T004, T007)

**Checkpoint**: All 4 new tests and all 18 existing tests pass. Feature complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T011 [P] Run full test suite `python -m pytest tests/ -v` and confirm all tests pass (zero regressions; total count ≥ 22)
- [X] T012 [P] Update `SECOND_ROADMAP.md` to mark schema versioning complete and advance the persistence milestone marker

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **User Story 1 (Phase 3)**: Depends on T001–T002 (fixture must exist before tests run)
- **User Story 2 (Phase 4)**: Can start after Phase 1; no dependency on US1
- **User Story 3 (Phase 5)**: Depends on T004 (save_version read) and T007 (SCHEMA_VERSION constant)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on fixture (T002); no code dependency on US2 or US3
- **US2 (P2)**: No dependency on US1; needs SCHEMA_VERSION constant (T007)
- **US3 (P3)**: Depends on T004 (from US1 impl) and T007 (from US2 impl)

### Within Each User Story

- TEST-AGENT writes tests first; IMPL-AGENT confirms they fail, then implements
- Implementation tasks within a story execute in listed order
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel (T002 only needs the directory to exist first — run sequentially)
- T005 and T006 can be written in parallel (same file, but TEST-AGENT handles both)
- T007 (constant) can be added before or alongside T005/T006 tests if IMPL-AGENT starts early
- T011 and T012 can run in parallel in the Polish phase

---

## Parallel Example: User Story 2

```
# TEST-AGENT writes both tests together:
Task T005: "Write test_save_includes_schema_version in tests/test_schema_version.py"
Task T006: "Write test_save_schema_version_is_1 in tests/test_schema_version.py"

# Once tests are confirmed failing, IMPL-AGENT implements in order:
Task T007: "Add SCHEMA_VERSION constant to game_state.py"
Task T008: "Update save() to write schema_version key"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create fixture files
2. Complete Phase 3: Write T003 test; implement T004 in `game_state.py`
3. **STOP and VALIDATE**: Run `python -m pytest tests/ -v` — confirms regression guard active
4. US1 delivered: legacy saves will never silently break

### Incremental Delivery

1. Phase 1 + Phase 3 (US1) → Regression guard in place (**MVP**)
2. Phase 4 (US2) → New saves stamped with version
3. Phase 5 (US3) → Newer-version saves safely rejected
4. Phase 6 → Full validation + roadmap update

### Full Feature (Single Session)

All 12 tasks can be completed in one session. With correct agent separation:
- TEST-AGENT session: T003, T005, T006, T009 (all test writing)
- IMPL-AGENT session: T004, T007, T008, T010 (all implementation)
- Orchestrator: T001, T002, T011, T012

---

## Notes

- `game_state.py` is the only source file modified — changes are additive only
- `tests/test_schema_version.py` is a new test file; `tests/test_state.py` is unchanged
- `tests/fixtures/legacy_save_v0.json` must reference a real `.dngn` file; use `DebugMapLoader.dngn`
- `STATE_FILE` monkeypatching pattern already used in `test_state.py` — follow the same fixture setup
- No new runtime dependencies; no `requirements.txt` change needed
- Each user story can be demoed independently; US1 can ship alone as the regression guard
