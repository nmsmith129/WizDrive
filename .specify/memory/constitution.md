<!--
SYNC IMPACT REPORT
==================
Version change: 1.3.1 → 2.0.0
Bump rationale: MAJOR — backward-incompatible redefinition of an existing governance
constraint. The mandated dependency-declaration artifact changes from requirements.txt
to pyproject.toml, and requirements.txt is removed from the repository. A repository
that was compliant under 1.3.1 (requirements.txt present, declaring runtime deps) is no
longer compliant, which the versioning policy classifies as a backward-incompatible
change.
  - Technology & Architecture Constraints (Runtime): runtime external dependencies MUST
    now be declared in pyproject.toml ([project.dependencies]); test-only dependencies
    (e.g. pytest) belong in an optional-dependencies group and remain exempt.
  - Definition of Done: dependency-declaration item now points at pyproject.toml.

Principles:
  I–VI. Unchanged.

Added sections: none
Removed sections: none

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  (Constraints gate: requirements.txt → pyproject.toml)

Follow-up TODOs: none
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.3.0 → 1.3.1
Bump rationale: PATCH — clarification of dependency policy: test-only dependencies
(e.g. pytest) are exempt from the requirements.txt declaration rule. Only runtime
external dependencies must be declared. The Definition of Done checklist updated to
match. No principles added or redefined; no templates require changes.

Principles:
  I–VI. Unchanged.

Added sections: none
Removed sections: none

Templates requiring updates: none

Follow-up TODOs: none new (existing open TODOs from 1.3.0 unchanged)
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.2.0 → 1.3.0
Bump rationale: MINOR — clarifications and new guidance, no backward-incompatible
removal/redefinition:
  - Dependency policy: pygame is no longer "the only" dependency; ALL external
    dependencies MUST be declared in requirements.txt.
  - Principle V: now requires a `schema_version` field in game_state.json and a
    regression test that loads an older-version save fixture.
  - Principle VI: scoped to AI-assisted development (human-written code is exempt);
    Opus permitted per-task only with explicit prior user permission; added an
    explicit enforcement note (no runtime guard; verified at plan gate + review).
  - Added "Target platforms: Windows and Linux" with msvcrt flagged as debt.
  - Added new section: Definition of Done.
  - Added new section: Glossary (orchestrator, sub-agent, implementation/testing
    sub-agent).

Principles:
  I.   Test-First Discipline (NON-NEGOTIABLE)        (unchanged)
  II.  Data-Driven Content                            (unchanged)
  III. Rendering-Agnostic Core                        (unchanged)
  IV.  Consistent Code Style                           (unchanged)
  V.   Backward-Compatible Persistence                 (EXPANDED: schema_version + regression test)
  VI.  Sub-Agent Execution & Test Independence         (CLARIFIED: scope, Opus escalation, enforcement)

Added sections: Definition of Done; Glossary
Removed sections: none

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  (Constitution Check gates V & VI + constraints line)
  ✅ .specify/templates/tasks-template.md (Opus-with-permission note)
  ✅ .specify/templates/spec-template.md  (reviewed — no change needed)

Follow-up TODOs (implementation work the new rules now require):
  - TODO(REQUIREMENTS): No requirements.txt exists yet; create one declaring pygame and pytest.
  - TODO(SCHEMA_VERSION): game_state.json has no schema_version field yet; add it.
  - TODO(SAVE_REGRESSION): Add a regression test that loads an older-version save fixture.
  - TODO(MSVCRT): text_visualizer real-time input uses Windows-only msvcrt; add a Linux path.
  - TODO(GUIDANCE_FILE): RESOLVED — CLAUDE.md restored at repo root and updated.
-->

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

Save/load MUST tolerate older save files:

- `game_state.json` MUST include a `schema_version` field identifying the save format.
- `GameState.from_save()` MUST read each field with a defaulting accessor
  (`.get(field, default)`) so pre-existing saves keep loading after new fields are added.
- A regression test MUST load a saved older-version fixture and assert it restores
  correctly.
- Removing or repurposing a persisted field is a breaking change: it MUST be called out
  explicitly and reflected in a `schema_version` bump.

**Rationale:** Players keep their saves across versions; silent save breakage is
unacceptable, and a version field makes compatibility provable rather than assumed.

### VI. Sub-Agent Execution & Test Independence

This principle governs **AI-assisted development**. Code written directly by a human
developer is outside its scope and is never a violation.

During AI-assisted development, all feature implementation and all test-writing/
test-execution MUST be delegated to sub-agents. The orchestrating agent MUST NOT write
feature code or tests directly — it only plans, delegates, and reviews.

- Implementation work is delegated to one or more **implementation sub-agents**.
- Test-writing and execution are delegated to a separate **testing sub-agent**; per
  Principle I it writes the tests first, so they fail before implementation exists.
- The testing sub-agent and the implementation sub-agent MUST be distinct invocations.
  The implementation sub-agent MUST NOT write or modify its own tests; any test change
  is made by the testing sub-agent.
- Every implementation and testing sub-agent runs the **Sonnet** model by default. A
  sub-agent MAY use **Opus** for a specific task when its difficulty warrants it, but
  ONLY after explicit permission is obtained from the user beforehand, with the
  escalation recorded in the plan's Complexity Tracking.

**Enforcement:** There is no runtime guard for this principle. Compliance is verified at
the plan-gate Constitution Check and during human review of the implementation.

**Rationale:** Independent verification removes confirmation bias — an implementer who
writes their own tests encodes the same wrong assumptions into both. Standardizing on
Sonnet keeps cost and behaviour consistent for high-volume work, while gated Opus
escalation preserves an escape hatch for genuinely hard problems.

## Technology & Architecture Constraints

- **Runtime:** Python 3.11+. Dependencies beyond `pygame` are permitted. Every runtime
  external dependency MUST be declared in `pyproject.toml` (`[project.dependencies]`) at
  the repository root; test-only dependencies (e.g. `pytest`) belong in an
  optional-dependencies group (e.g. `[project.optional-dependencies].dev`) and are exempt
  from the runtime-declaration requirement. `pyproject.toml` MUST also set
  `requires-python = ">=3.11"`. Adding a new runtime dependency MUST be justified in the
  feature plan.
- **Target platforms:** Windows and Linux. Platform-specific code MUST be isolated and
  provide a path for both. The text visualizer's real-time key input uses `msvcrt`,
  which is Windows-only; this is acknowledged technical debt and MUST gain a Linux
  equivalent to satisfy the Linux target.
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
  testing to sub-agents running the Sonnet model (Opus only with prior user permission);
  test tasks and implementation tasks go to separate sub-agents (Principle VI).
- **Merge gate:** The full pytest suite (`python -m pytest tests/ -v`) MUST pass
  before any merge into `main`.
- **Roadmap order:** New features SHOULD respect the dependency ordering captured in
  `docs/SECOND_ROADMAP.md` — do not build a feature ahead of its prerequisites. *(Advisory.)*

## Definition of Done

A feature is Done only when ALL of the following hold:

- [ ] All new behaviour has tests (Principle I), authored by the testing sub-agent
      (Principle VI).
- [ ] The full pytest suite passes (`python -m pytest tests/ -v`).
- [ ] The plan's Constitution Check gate passed; any deviation is justified in the
      plan's Complexity Tracking.
- [ ] Any new runtime external dependency is declared in `pyproject.toml`.
- [ ] Persistence changes carry a `schema_version` update and a save regression test
      (Principle V), where applicable.
- [ ] Documentation is updated — `CLAUDE.md` and the relevant `docs/SECOND_ROADMAP.md`
      markers.
- [ ] Work is merged into `working` (and into `main` at milestones).

## Glossary

- **Orchestrator (orchestrating agent):** the top-level agent that plans, delegates to
  sub-agents, and reviews their output. During AI-assisted development it does not write
  feature code or tests directly.
- **Sub-agent:** a separate, isolated agent invocation spawned by the orchestrator to
  perform a delegated task with its own context.
- **Implementation sub-agent:** a sub-agent that writes feature/production code.
- **Testing sub-agent:** a sub-agent that writes and runs tests, distinct from any
  implementation sub-agent.

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
  `CLAUDE.md`.

**Version**: 2.0.0 | **Ratified**: 2026-06-07 | **Last Amended**: 2026-06-21
