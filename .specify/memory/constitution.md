<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 3.0.0
Bump rationale: MAJOR — backward-incompatible redefinition of nearly every principle's
technology binding, plus a scope change to Principle VI. WizDrive has been ported from
Python/Pygame to Godot 4.7 / GDScript (Python source archived under archive/). Every
principle and constraint that named a Python tool, filetype, or API is re-grounded in its
Godot equivalent; pygame-implementation-only constraints are dropped; Principle VI gains a
guided-learning carve-out. A repository/plan compliant under 2.0.0 (Python, pytest,
pyproject.toml) is no longer compliant, which the versioning policy classifies as MAJOR.

Principles:
  I.   Test-First Discipline (NON-NEGOTIABLE)   (RE-GROUNDED: pytest → GUT; map loader →
       DungeonData resources; deterministic randf())
  II.  Data-Driven Content                       (RE-GROUNDED: ENEMY_TYPES/ITEM_TYPES →
       TypeLibrary + .tres; .dngn → DungeonData .tres)
  III. Rendering-Agnostic Core                   (RE-GROUNDED: pygame → Node/scene deps)
  IV.  Consistent Code Style                      (RE-GROUNDED: Python style → GDScript style)
  V.   Backward-Compatible Persistence            (RE-GROUNDED: game_state.json → SaveGame
       resource via ResourceSaver)
  VI.  Sub-Agent Execution & Test Independence    (SCOPE CHANGE: added guided-learning
       carve-out)

Added sections: none
Removed sections: none

Dropped constraints (pygame-only artifacts, no honest Godot analog):
  - pygame.init() before map load (Enemy/Item are RefCounted, no Surface)
  - map_loader.debug flag (no such flag in the port)
  - FloorData positional-tuple unpacking (FloorData is now a Resource; inverted to
    named-property access)
  - msvcrt Windows-only text-input technical-debt clause (Godot exports cross-platform)

Note: historical pre-3.0.0 Sync Impact Reports removed to keep the active governance file
free of stale Python references; version history is preserved in git.

Templates requiring updates:
  ✅ .specify/templates/plan-template.md  (Constitution Check gate + Technical Context
     examples re-grounded to Godot/GUT/GDScript)
  ✅ .specify/templates/spec-template.md  (verified — no Python references, no change)
  ✅ .specify/templates/tasks-template.md (verified — no Python references, no change)

Follow-up TODOs: none
-->

# WizDrive Constitution

## Core Principles

### I. Test-First Discipline (NON-NEGOTIABLE)

The GUT (Godot Unit Test) suite is the safety net for an evolving game and MUST stay green
on every commit that merges to `main`. New behaviour MUST ship with tests:

- Map/data changes MUST exercise loading AND validation of the affected `DungeonData`
  `.tres` resources (via `load()`/`ResourceLoader`).
- Combat, XP/leveling, and state changes MUST have coverage in the corresponding `test/`
  suite.
- Probabilistic logic MUST be made deterministic in tests — seed the RNG or inject a
  `RandomNumberGenerator` double so `randf()` is repeatable (mirrors the old
  `always_hit`/`always_miss` fixtures).

Run the suite headless with:
`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`.

**Rationale:** The project already carries a large automated suite (ported from pytest);
preserving it is the cheapest defense against regressions as systems are added.

### II. Data-Driven Content

Game content MUST be expressed as data, not hardcoded into game logic. Enemies and items
come from the `TypeLibrary` autoload backed by `EnemyType`/`ItemType` `.tres` resources
under `resources/`; dungeons come from `DungeonData` `.tres` resources under `data/maps/`.
New content types MUST extend those resources or the map resource schema — with a
documented default fallback for unknown names — rather than branching logic per item.

**Rationale:** Content scales without code changes and stays testable in isolation.

### III. Rendering-Agnostic Core

Core game logic (`Player`, `GameState`, and `DungeonData` loading) MUST remain independent
of any specific view, and free of `Node`/scene/rendering dependencies where avoidable —
core classes extend `RefCounted`, not `Node` (`Player` does this today). Every view (2D
parity view, first-person `FloorView3D`, text) MUST consume the same shared state through
the same public API, communicating via signals rather than reaching into rendering nodes.

**Rationale:** Keeps the planned first-person renderer additive and lets logic be tested
headless.

### IV. Consistent Code Style

Code MUST follow the established GDScript conventions:

- Godot 4.7 with typed GDScript throughout; `class_name` + `extends` for named types.
- `.gd` file names are `snake_case`; `class_name` identifiers are `PascalCase`; functions
  and variables are `snake_case`; constants are `UPPER_SNAKE_CASE`; private functions use a
  `_leading_underscore`; signals are past-tense (`attacked`, `defeated`); constructor
  parameters use a `p_` prefix to avoid shadowing members.
- Comments are single-line `#` on the first line of a function body for non-obvious logic
  only — never on obvious code. `##` is reserved for documentation comments on scripts,
  members, and signals.
- Error/log messages MUST quote untrusted/user-supplied values (wrap in quotes or use
  `var_to_str()`); GDScript has no `!r`, so the quoting must be explicit.

**Rationale:** Uniform style keeps a multi-client, multi-session codebase readable.

### V. Backward-Compatible Persistence

Save/load MUST tolerate older save files:

- The save is a `SaveGame` resource written via `ResourceSaver` (e.g.
  `user://savegame.tres`) and MUST include an exported `schema_version: int` identifying
  the save format.
- Loading MUST rely on the fact that exported Resource properties auto-default when absent,
  so pre-existing saves keep loading after new fields are added; any custom load path MUST
  apply an equivalent default rather than assuming a field is present.
- A regression test MUST load a saved older-version fixture resource and assert it restores
  correctly.
- Removing or repurposing a persisted field is a breaking change: it MUST be called out
  explicitly and reflected in a `schema_version` bump.

**Rationale:** Players keep their saves across versions; silent save breakage is
unacceptable, and a version field makes compatibility provable rather than assumed.

### VI. Sub-Agent Execution & Test Independence

This principle governs **AI-assisted development**. Code written directly by a human
developer is outside its scope and is never a violation. In particular, **guided-learning
work** — where the user writes GDScript directly while the agent only explains, reviews,
and advises (not delegating implementation) — is explicitly exempt from the sub-agent
delegation mandate below. The Sonnet-default / gated-Opus rule still governs any actual
sub-agent delegation that does occur.

During delegated AI-assisted development, all feature implementation and all test-writing/
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
escalation preserves an escape hatch for genuinely hard problems. The guided-learning
carve-out keeps the constitution honest about how the port is actually being built.

## Technology & Architecture Constraints

- **Engine:** Godot 4.7 (GL Compatibility renderer), GDScript. The engine version is
  recorded in `project.godot` (`config/features`). Adding a new engine feature/renderer
  dependency MUST be justified in the feature plan.
- **Third-party dependencies:** Any third-party addon/plugin MUST be committed under
  `addons/` and enabled in `project.godot`. Dev-only addons (e.g. GUT) are the testing
  equivalent of test-only dependencies and are exempt from the runtime-justification
  requirement, but MUST still be committed so the suite runs reproducibly.
- **Target platforms:** Windows and Linux. Godot exports cross-platform natively;
  platform-specific code (if any) MUST be isolated and provide a path for both.
- **Data access:** `DungeonData`, `FloorData`, `EnemyType`, and `ItemType` are Resource
  classes — access their fields by name (`floor.grid`, `floor.player_start`, …). Do not
  reintroduce positional-tuple unpacking for floor/map data.
- **Debug output:** Committed game-path code MUST NOT leave verbose debug `print()` output
  enabled; gate diagnostics behind an explicit debug flag or remove them before merge.
- **Generated artifacts:** The save resource lives under `user://` (outside the repo). The
  Godot cache (`.godot/`) and import metadata (`.import/`) are git-ignored and MUST NOT be
  committed.

## Development Workflow & Quality Gates

- **Spec-Driven Development:** Features follow the cycle
  `specify → clarify → plan → tasks → implement`, honoring the review gates after the
  spec and plan phases.
- **Branching:** Feature work happens on sequentially numbered feature branches cut
  from the integration branch. Completed features are merged into `main` at milestones.
- **Agent separation:** During delegated `implement` work, the orchestrator delegates ALL
  coding and testing to sub-agents running the Sonnet model (Opus only with prior user
  permission); test tasks and implementation tasks go to separate sub-agents (Principle
  VI). Guided-learning work is exempt (Principle VI carve-out).
- **Merge gate:** The full GUT suite
  (`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`) MUST pass
  before any merge into `main`.
- **Roadmap order:** New features SHOULD respect the dependency ordering captured in
  `docs/SECOND_ROADMAP.md` — do not build a feature ahead of its prerequisites. *(Advisory.)*

## Definition of Done

A feature is Done only when ALL of the following hold:

- [ ] All new behaviour has tests (Principle I), authored by the testing sub-agent
      (Principle VI) — unless produced as guided-learning work.
- [ ] The full GUT suite passes
      (`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`).
- [ ] The plan's Constitution Check gate passed; any deviation is justified in the
      plan's Complexity Tracking.
- [ ] Any new third-party addon is committed under `addons/` and enabled in `project.godot`.
- [ ] Persistence changes carry a `schema_version` update and a save regression test
      (Principle V), where applicable.
- [ ] Documentation is updated — `CLAUDE.md` and the relevant `docs/SECOND_ROADMAP.md`
      markers.
- [ ] Work is merged into the integration branch (and into `main` at milestones).

## Glossary

- **Orchestrator (orchestrating agent):** the top-level agent that plans, delegates to
  sub-agents, and reviews their output. During delegated AI-assisted development it does
  not write feature code or tests directly.
- **Sub-agent:** a separate, isolated agent invocation spawned by the orchestrator to
  perform a delegated task with its own context.
- **Implementation sub-agent:** a sub-agent that writes feature/production code.
- **Testing sub-agent:** a sub-agent that writes and runs tests, distinct from any
  implementation sub-agent.
- **Guided-learning work:** development where the user writes GDScript directly and the
  agent only explains, reviews, and advises — exempt from the sub-agent mandate (Principle
  VI).

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

**Version**: 3.0.0 | **Ratified**: 2026-06-07 | **Last Amended**: 2026-07-05
