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

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Confirm this plan complies with the WizDrive Constitution (`.specify/memory/constitution.md`).
Mark each gate PASS / FAIL (justify any FAIL in Complexity Tracking):

- [ ] **I. Test-First (NON-NEGOTIABLE)**: New behaviour ships with pytest coverage; parser
      changes cover `load_map_file`/`validate_map_file`/`load_map_text`; probabilistic logic
      is made deterministic in tests.
- [ ] **II. Data-Driven Content**: New enemies/items/maps extend `ENEMY_TYPES`/`ITEM_TYPES`
      or the `.dngn` format (with fallbacks) rather than hardcoding content into logic.
- [ ] **III. Rendering-Agnostic Core**: Game logic stays visualizer-independent and avoids a
      `pygame` dependency where possible; all visualizers consume the same shared state.
- [ ] **IV. Consistent Code Style**: Python 3.11+, type hints, snake_case/PascalCase/UPPER_SNAKE
      naming, single-line first-line comments, `!r` for untrusted values.
- [ ] **V. Backward-Compatible Persistence**: Save/load tolerates older `game_state.json` via
      defaulting field access; `game_state.json` carries a `schema_version`; a regression test
      loads an older-version save fixture; breaking persisted-field changes bump `schema_version`.
- [ ] **VI. Sub-Agent Execution & Test Independence**: Plan delegates ALL implementation and
      testing to sub-agents (orchestrator only plans/reviews); test and implementation work go
      to separate sub-agents; sub-agents run Sonnet by default (Opus only with explicit prior
      user permission, recorded in Complexity Tracking).
- [ ] **Constraints**: Any new external dependency is declared in `requirements.txt`; new
      platform-specific code provides both a Windows and a Linux path.

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
