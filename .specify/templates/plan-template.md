# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Godot 4.7 / GDScript or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., Godot engine, GUT (dev-only addon) or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., SaveGame resource via ResourceSaver (user://), .tres data or N/A]

**Testing**: [e.g., GUT (godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit) or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Confirm this plan complies with the WizDrive Constitution (`.specify/memory/constitution.md`).
Mark each gate PASS / FAIL (justify any FAIL in Complexity Tracking):

- [ ] **I. Test-First (NON-NEGOTIABLE)**: New behaviour ships with GUT coverage; map/data
      changes cover loading AND validation of the affected `DungeonData` `.tres`; probabilistic
      logic is made deterministic in tests (seed the RNG or inject a `RandomNumberGenerator`).
- [ ] **II. Data-Driven Content**: New enemies/items/maps extend the `TypeLibrary`
      `EnemyType`/`ItemType` `.tres` or the `DungeonData` resource schema (with fallbacks)
      rather than hardcoding content into logic.
- [ ] **III. Rendering-Agnostic Core**: Game logic stays view-independent and avoids
      `Node`/scene/rendering dependencies where possible (core extends `RefCounted`); all views
      consume the same shared state.
- [ ] **IV. Consistent Code Style**: Godot 4.7 / typed GDScript, `class_name`+`extends`,
      snake_case files/funcs/vars, PascalCase `class_name`, UPPER_SNAKE constants,
      `_leading_underscore` privates, `#`/`##` comment discipline, quoted untrusted values.
- [ ] **V. Backward-Compatible Persistence**: Save/load tolerates older saves via defaulting
      Resource properties; the `SaveGame` resource carries a `schema_version`; a regression test
      loads an older-version save fixture; breaking persisted-field changes bump `schema_version`.
- [ ] **VI. Sub-Agent Execution & Test Independence**: Delegated work sends ALL implementation
      and testing to sub-agents (orchestrator only plans/reviews); test and implementation work
      go to separate sub-agents; sub-agents run Sonnet by default (Opus only with explicit prior
      user permission, recorded in Complexity Tracking). Guided-learning work is exempt.
- [ ] **Constraints**: Any new third-party addon is committed under `addons/` and enabled in
      `project.godot`; new platform-specific code provides both a Windows and a Linux path.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
