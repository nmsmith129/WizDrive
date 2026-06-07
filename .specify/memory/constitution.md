<!--
SYNC IMPACT REPORT
==================
Version change: 1.1.0 → 1.2.0
Bump rationale: MINOR — materially expanded Principle VI. It now requires that ALL
implementation and ALL testing/test-writing be delegated to sub-agents (the
orchestrating agent only plans, delegates, and reviews), and that every such
implementation and testing sub-agent run the Sonnet model. Principle renamed from
"Independent Test Authorship" to "Sub-Agent Execution & Test Independence" to reflect
the broadened scope. No principles removed; no backward-incompatible redefinition.

Principles:
  I.   Test-First Discipline (NON-NEGOTIABLE)        (unchanged)
  II.  Data-Driven Content                            (unchanged)
  III. Rendering-Agnostic Core                        (unchanged)
  IV.  Consistent Code Style                           (unchanged)
  V.   Backward-Compatible Persistence                 (unchanged)
  VI.  Sub-Agent Execution & Test Independence         (EXPANDED in 1.2.0; was
       "Independent Test Authorship")

Added sections: none
Removed sections: none

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  (Constitution Check gate VI updated)
  ✅ .specify/templates/tasks-template.md (agent-separation note: sub-agents + Sonnet)
  ✅ .specify/templates/spec-template.md  (reviewed — no change needed)

Follow-up TODOs:
  - TODO(GUIDANCE_FILE): Runtime guidance should live in CLAUDE.md at the repo root,
    but that file currently exists only as CLAUDE_old.md AND contains unresolved Git
    conflict markers (<<<<<<< / ======= / >>>>>>>). Resolve and restore CLAUDE.md.
-->

# WizDrive Constitution

## Core Principles

### I. Test-First Discipline (NON-NEGOTIABLE)

The pytest suite is the safety net for an evolving game and MUST stay green on every
commit that merges to `main`. New behaviour MUST ship with tests:

- Map/parser changes MUST exercise all relevant paths — `load_map_file`,
  `validate_map_file`, and `load_map_text`.
- Combat, XP/leveling, and state changes MUST have coverage in the corresponding
  `tests/` module.
- Probabilistic logic MUST be made deterministic in tests (e.g. monkeypatch
  `player.random.random` via the `always_hit`/`always_miss` fixtures).

**Rationale:** The project already carries a large automated suite; preserving it is
the cheapest defense against regressions as systems are added.

### II. Data-Driven Content

Game content MUST be expressed as data, not hardcoded into game logic. Enemies and
items come from the `ENEMY_TYPES` and `ITEM_TYPES` lookup tables; dungeons come from
`.dngn` files. New content types MUST extend these tables or the map format — with a
documented default fallback for unknown names — rather than branching logic per item.

**Rationale:** Content scales without code changes and stays testable in isolation.

### III. Rendering-Agnostic Core

Core game logic (`Player`, `GameState`, `map_loader`) MUST remain independent of any
specific visualizer, and free of a `pygame` dependency where avoidable (`Player` has
none today). Every visualizer (pygame top-down, text/ASCII, future first-person 3D)
MUST consume the same shared state through the same public API.

**Rationale:** Keeps the planned 3D renderer additive and lets logic be tested headless.

### IV. Consistent Code Style

Code MUST follow the established conventions:

- Python 3.11+ with type hints throughout; `from __future__ import annotations` for
  forward references.
- `snake_case` for modules/functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants, `_leading_underscore` for module-private functions.
  Module files stay `snake_case` even when they contain a `PascalCase` class.
- Comments are single-line (`# ...`) on the first line of a method body for
  non-obvious logic only — not docstrings, and never on obvious code.
- Error messages use `!r` (repr) formatting for untrusted/user-supplied values.

**Rationale:** Uniform style keeps a multi-client, multi-session codebase readable.

### V. Backward-Compatible Persistence

Save/load MUST tolerate older save files. `GameState.from_save()` MUST read each field
with a defaulting accessor (`.get(field, default)`) so pre-existing `game_state.json`
files keep loading after new fields are added. Removing or repurposing a persisted
field is a breaking change and MUST be called out explicitly.

**Rationale:** Players keep their saves across versions; silent save breakage is
unacceptable.

### VI. Sub-Agent Execution & Test Independence

All feature implementation and all test-writing/test-execution MUST be delegated to
sub-agents. The orchestrating agent MUST NOT write feature code or tests directly — it
only plans, delegates, and reviews.

- Implementation work is delegated to one or more **implementation sub-agents**.
- Test-writing and test execution are delegated to a separate **testing sub-agent**;
  per Principle I it writes the tests first, so they fail before implementation exists.
- The testing sub-agent and the implementation sub-agent MUST be distinct invocations.
  The implementation sub-agent MUST NOT write or modify its own tests; any test change
  is made by the testing sub-agent.
- Every implementation and testing sub-agent MUST run the **Sonnet** model.

**Rationale:** Independent verification removes confirmation bias — an implementer who
writes their own tests encodes the same wrong assumptions into both. Mandating
delegation keeps that separation enforceable, and standardizing on Sonnet for the
high-volume implementation/testing work keeps cost and behaviour consistent while the
orchestrator handles planning and review.

## Technology & Architecture Constraints

- **Runtime:** Python 3.11+. `pygame` is the only permitted external dependency;
  adding a new third-party dependency MUST be justified in the feature plan.
- **Pygame lifecycle:** `pygame.init()` MUST run before any map is loaded, because
  `Enemy`/`Item` allocate `pygame.Surface` objects in `__init__`.
- **Debug output:** `map_loader.debug` MUST be set to `False` in every entry-point
  file before calling any loader function. Committed game-path code MUST NOT leave it
  `True`.
- **FloorData:** the positional `FloorData` tuple MUST be unpacked with named
  variables (`grid, start_pos, start_facing, enemies, items, stairs = floor`).
- **Generated artifacts:** `game_state.json` and bytecode (`__pycache__/`) are
  git-ignored and MUST NOT be committed.

## Development Workflow & Quality Gates

- **Spec-Driven Development:** Features follow the cycle
  `specify → clarify → plan → tasks → implement`, honoring the review gates after the
  spec and plan phases.
- **Branching:** Feature work happens on sequentially numbered feature branches cut
  from `working`. Completed features are merged into `main` at milestones; `working`
  is the integration branch.
- **Agent separation:** During `implement`, the orchestrator delegates ALL coding and
  testing to sub-agents running the Sonnet model; test tasks and implementation tasks
  go to separate sub-agents (Principle VI).
- **Merge gate:** The full pytest suite (`python -m pytest tests/ -v`) MUST pass
  before any merge into `main`.
- **Roadmap order:** New features SHOULD respect the dependency ordering captured in
  `SECOND_ROADMAP.md` — do not build a feature ahead of its prerequisites.

## Governance

This constitution supersedes other practices when they conflict. Amendments MUST be
made by editing this file, bumping the version per the policy below, and synchronizing
the dependent templates listed in the Sync Impact Report.

- **Versioning policy (semantic):** MAJOR for backward-incompatible governance or
  principle removals/redefinitions; MINOR for a new principle/section or materially
  expanded guidance; PATCH for clarifications and non-semantic refinements.
- **Compliance:** Every implementation plan MUST pass the Constitution Check gate in
  `plan-template.md`. Any deviation MUST be recorded in that plan's Complexity
  Tracking table with a justification and the rejected simpler alternative.
- **Runtime guidance:** Day-to-day development guidance lives in the repository-root
  `CLAUDE.md` (see follow-up TODO in the Sync Impact Report regarding its current state).

**Version**: 1.2.0 | **Ratified**: 2026-06-07 | **Last Amended**: 2026-06-07
