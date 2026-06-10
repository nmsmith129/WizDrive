# Feature Specification: Persistence Schema Versioning

**Feature Branch**: `001-persistence-schema-versioning`

**Created**: 2026-06-07

**Status**: Draft

**Input**: User description: "Add schema_version to game_state.json and a save-compatibility regression test"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saved games survive game updates (Priority: P1)

A returning player loads a game they saved before updating WizDrive. The save was
created by an earlier version that did not track a save format. The game loads it
without errors and the character resumes with all prior progress intact.

**Why this priority**: This is the whole point of the feature — players must never lose
progress to an update. Without it, every change to the save format risks breaking
existing saves.

**Independent Test**: Take a save file produced by a pre-versioning build, load it in
the current build, and verify location, facing, HP/MP, XP, level, and all six
attributes restore to their saved values.

**Acceptance Scenarios**:

1. **Given** a save file with no version marker, **When** the player loads it, **Then** the game restores all character state and continues without error.
2. **Given** a save file missing newly added fields, **When** it is loaded, **Then** the missing fields take sensible defaults and the rest restore correctly.

---

### User Story 2 - Save files identify their format (Priority: P2)

When the game writes a save, it stamps the file with the format version it was written
in, so the game can make correct decisions when reading it later.

**Why this priority**: Enables safe evolution of the save format and is a prerequisite
for any future migration or compatibility warnings.

**Independent Test**: Save a game, inspect the save file, confirm it carries a version
identifier, then reload it and confirm it restores correctly.

**Acceptance Scenarios**:

1. **Given** a newly saved game, **When** the save is written, **Then** it includes a format version identifier.
2. **Given** a save written by the current version, **When** it is reloaded by the current version, **Then** it restores with no warnings.

---

### User Story 3 - Clear handling of newer/unreadable saves (Priority: P3)

If a player tries to load a save written by a newer version than they are running, the
game does not silently misread it; it reports that the save is too new instead of
loading corrupted state.

**Why this priority**: Prevents silent data corruption in a less common but damaging
scenario (e.g. after a downgrade or sharing saves between versions).

**Independent Test**: Craft a save whose version is higher than the current format,
attempt to load it, and verify the game declines with a clear message rather than
loading partial state.

**Acceptance Scenarios**:

1. **Given** a save with a newer format version, **When** the player loads it, **Then** the game declines and explains that the save is from a newer version, leaving the current game unaffected.

---

### Edge Cases

- Save with no version field (legacy) → treated as the earliest known version and loaded.
- Save with an unrecognized or corrupt version value → treated as invalid; the player is
  informed and the current game is unaffected.
- Save missing individual fields → per-field defaults are substituted (existing behavior
  preserved).
- A failed load → the on-disk save file is left untouched.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record a save-format version identifier — a positive integer starting at 1 — in every save file it writes.
- **FR-002**: The system MUST load save files that predate version tracking (no version field) without error, treating them as the earliest format.
- **FR-003**: The system MUST restore all persisted character state — location, facing, HP, MP, XP, level, and the six attributes — from any supported save version.
- **FR-004**: When a persisted field is absent, the system MUST substitute a documented default and continue loading.
- **FR-005**: The system MUST decline to load a save whose format version (integer) is greater than the version it supports, informing the player rather than loading partial or incorrect state.
- **FR-006**: A failed load MUST be non-destructive — the on-disk save file MUST NOT be overwritten when it cannot be loaded.
- **FR-007**: Save compatibility MUST be covered by an automated regression test that loads an older-version save fixture and asserts correct restoration.

### Key Entities

- **Save File** (`game_state.json`): the persisted snapshot of a game. Holds a format
  version identifier (a positive integer, starting at 1 for the initial schema) plus all
  player state fields. Written by the save action and consumed by the load action.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of save files created by prior versions load successfully in the current version with no loss of character state.
- **SC-002**: Every save written by the current version carries a format version identifier (verifiable by inspecting the file).
- **SC-003**: Loading a save from a newer format version fails safely — clear message, no corrupted state — in 100% of attempts.
- **SC-004**: Automated save-compatibility coverage exists and passes as part of the standard test run.
- **SC-005**: No regression in existing load behavior — every previously loadable save remains loadable.

## Assumptions

- The save format is the single-file `game_state.json` described in `CLAUDE.md`.
- "Older version" includes pre-versioning saves with no version field; these are treated
  as the earliest version.
- The default policy for newer-than-supported saves is to decline loading (safest);
  building migration tooling is out of scope for this feature.
- Forward migration of very old saves beyond default-filling is out of scope; the current
  per-field default behavior is retained.
- Only one save file/slot is in scope (multiple save slots are a separate roadmap item).

## Clarifications

### Session 2026-06-10

- Q: What format should the version identifier take in the save file? → A: Integer, starting at 1.
