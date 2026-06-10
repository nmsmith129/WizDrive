# Implementation Plan: Persistence Schema Versioning

**Branch**: `001-persistence-schema-versioning` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-persistence-schema-versioning/spec.md`

## Summary

Add `schema_version` (positive integer, starting at 1) to `game_state.json` and update
`GameState.from_save()` to reject saves from newer-than-supported versions while
accepting legacy saves (no version field, treated as version 0) with existing defaults.
Deliver an automated regression test loading a v0 fixture and asserting full state
restoration.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `pygame` (runtime, in `requirements.txt`); `pytest` (test
only — exempt from `requirements.txt` per Constitution v1.3.1)

**Storage**: `game_state.json` — flat JSON, single save slot, path held in `STATE_FILE`
constant in `game_state.py`

**Testing**: pytest (`python -m pytest tests/ -v`)

**Target Platform**: Windows + Linux — save/load uses stdlib `json` only; platform-neutral

**Project Type**: Desktop game (dungeon crawler)

**Performance Goals**: N/A — save/load is a one-time I/O operation per session

**Constraints**: No new runtime dependencies; all existing saves must remain loadable

**Scale/Scope**: Single save file, ~20 persisted fields, ~18 existing tests in
`test_state.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Test-First (NON-NEGOTIABLE)**: FR-007 mandates a save regression test; all
      new version-check logic ships with pytest coverage authored by the testing sub-agent.
- [x] **II. Data-Driven Content**: Not applicable — no new enemies, items, or maps.
- [x] **III. Rendering-Agnostic Core**: Changes touch only `game_state.py` save/load
      methods. No `pygame` dependency introduced.
- [x] **IV. Consistent Code Style**: `SCHEMA_VERSION` (UPPER_SNAKE_CASE), type hint
      `int`, `!r` in the error message, single-line method comment where non-obvious.
- [x] **V. Backward-Compatible Persistence**: This feature implements Principle V's
      `schema_version` requirement. Legacy saves (no field) default to version 0 and
      load via existing `.get()` defaults.
- [x] **VI. Sub-Agent Execution & Test Independence**: Implementation and testing go to
      separate sub-agents. Sonnet only — no Opus escalation needed.
- [x] **Constraints**: No new runtime dependency; stdlib `json` only; platform-neutral.

All gates **PASS**. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/001-persistence-schema-versioning/
├── plan.md          ← this file
├── research.md      ← Phase 0 output
├── data-model.md    ← Phase 1 output
├── quickstart.md    ← Phase 1 output
└── tasks.md         ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code Changes

```
game_state.py                     ← add SCHEMA_VERSION; update save() and from_save()
tests/
├── fixtures/
│   └── legacy_save_v0.json       ← new: minimal save without schema_version field
└── test_state.py                 ← add schema_version tests (or new test_schema_version.py)
```

No new top-level modules. `tests/fixtures/` is a new subdirectory.

**Structure Decision**: Flat-root layout matches the existing project (all source modules
at repo root, all tests under `tests/`). The `tests/fixtures/` subdirectory follows
pytest convention for static test data.

## Implementation Approach

### `game_state.py` — implementation sub-agent

1. Add module-level constant directly below the existing imports/constants:
   ```python
   SCHEMA_VERSION: int = 1
   ```

2. In `save()`, add `schema_version` as the first key in the dict written to `STATE_FILE`:
   ```python
   "schema_version": SCHEMA_VERSION,
   ```

3. In `from_save()`, immediately after `data = json.load(f)`:
   ```python
   save_version = data.get("schema_version", 0)
   if save_version > SCHEMA_VERSION:
       raise ValueError(
           f"Save is from a newer version of WizDrive "
           f"(save {save_version!r} > supported {SCHEMA_VERSION!r})."
       )
   ```
   No other changes to `from_save()` — all existing `.get()` defaults already handle v0.

### `tests/` — testing sub-agent

New tests (add to `test_state.py` or a new `test_schema_version.py`):

| Test | Description |
|------|-------------|
| `test_save_includes_schema_version` | Save → read JSON → assert `"schema_version"` key present |
| `test_save_schema_version_is_1` | Save → read JSON → assert value equals 1 |
| `test_legacy_v0_save_loads` | Load `fixtures/legacy_save_v0.json` → assert all fields restore |
| `test_newer_version_save_raises` | Load save with `schema_version=2` → assert `ValueError` |

Fixture `tests/fixtures/legacy_save_v0.json`: valid `game_state.json` snapshot (all
current fields, no `schema_version`) referencing `DebugMapLoader.dngn`. See
`data-model.md` for exact schema.

Existing 18 tests in `test_state.py` must continue to pass (no regressions).

## Complexity Tracking

> No Constitution violations — section intentionally empty.
