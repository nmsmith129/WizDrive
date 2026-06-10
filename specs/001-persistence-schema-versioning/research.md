# Research: Persistence Schema Versioning

**Date**: 2026-06-10 | **Plan**: [plan.md](plan.md)

All technical decisions were resolved from the feature spec, the clarification session,
and direct codebase analysis. No external research was required.

---

## Decision 1 — Version identifier type and starting value

**Decision**: Positive integer, starting at 1. Field name: `schema_version`.

**Rationale**: Integer comparison (`save_version > SCHEMA_VERSION`) requires no parsing
library. Incrementing integers are the standard approach for game save schemas (cf. Save
format versioning in Celeste, Terraria, and similar). The field name `schema_version`
matches the feature branch name and the original user description.

**Alternatives considered**:
- Semver string (`"1.0"`) — rejected: adds string-parsing complexity; semver semantics
  (major/minor/patch) are overkill for a single flat JSON file.
- Date string (`"20260607"`) — rejected: non-obvious comparison; requires knowing the
  date a schema was introduced rather than its ordinal position.

**Starting value**: 1, not 0. Version 0 is reserved to mean "no version field present"
(legacy saves), so the first explicitly versioned schema must be 1 to allow the
`data.get("schema_version", 0)` sentinel to work correctly.

---

## Decision 2 — Legacy save handling

**Decision**: Reads `data.get("schema_version", 0)`. If version is 0 (absent), proceeds
with existing load logic. No migration step required.

**Rationale**: The current `from_save()` already uses `.get()` with sensible defaults
for all optional fields (attack, strength, defense, max_hp, intelligence, mana, xp,
level, enemy xp). Legacy saves (pre-versioning) carry all required fields and missing
optional fields fall back to defaults. No data is lost.

**Alternatives considered**:
- Explicit migration function per version — rejected: unnecessary for v0→v1 since no
  fields changed; adds complexity deferred to a future version bump.

---

## Decision 3 — Newer-than-supported save handling

**Decision**: Raise `ValueError` with a human-readable message. The caller (game entry
point) catches it and prints to the console.

**Rationale**: Raising an exception is cleanly testable with `pytest.raises`. It
surfaces at the call site rather than silently returning `None`, which would require
every caller to null-check. The message uses `!r` on the version numbers per Principle
IV.

**Alternatives considered**:
- Return `None` — rejected: callers must handle None; current callers do not; would
  require changes beyond `game_state.py`.
- Print and raise — rejected: double-reporting; let the entry point decide how to present
  the error to the user.

---

## Decision 4 — Non-destructive load guarantee

**Decision**: No additional code needed. `from_save()` opens `STATE_FILE` read-only
(`open(STATE_FILE)` with no mode argument defaults to `"r"`). A `ValueError` raised
before any write leaves the file untouched. FR-006 is satisfied by the existing
implementation structure.

**Test coverage**: A test that asserts `from_save()` raises rather than writing will
implicitly verify this. An explicit file-integrity test (compare file contents before
and after a failed load attempt) may be added by the testing sub-agent if deemed
worthwhile.

---

## Decision 5 — Test fixture location

**Decision**: `tests/fixtures/legacy_save_v0.json` — a static JSON file committed to
the repo.

**Rationale**: Pytest's standard pattern for static test data is a `fixtures/`
subdirectory alongside the test files. A committed file is reproducible, readable in
code review, and does not require any setup to generate.

**Fixture content**: All 19 current fields (dungeon, floor, x, y, facing, hp, mp,
attack, strength, defense, max_hp, intelligence, mana, xp, level, enemies) — no
`schema_version`. Must reference `DebugMapLoader.dngn` (the minimal two-floor dungeon
already in the repo) so `load_map_file()` succeeds during the test.
