# Feature Specification: Item Pickup Mechanics

**Feature Branch**: `claude/feature-prioritization-s7mu2h`

**Created**: 2026-06-19

**Status**: Draft

**Input**: User description: "Spec out the item pickup feature — pickup into inventory
plus auto-equip weapons, with the inventory persisted across save/load."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Collect items by walking onto them (Priority: P1)

A player explores a floor and walks onto a tile holding an item. The item is added to
the player's belongings and disappears from the floor, so it is no longer rendered and
cannot be picked up twice.

**Why this priority**: This is the core of the feature — without collection, items on
the map are inert scenery. It turns existing item placement and rendering into an
actual interaction.

**Independent Test**: Place an item on an open tile, move the player onto that tile, and
verify the item is now in the player's inventory and gone from the floor's item list.

**Acceptance Scenarios**:

1. **Given** an item on an open tile ahead, **When** the player moves onto that tile, **Then** the item is added to the player's inventory and removed from the floor.
2. **Given** a tile holding more than one item, **When** the player moves onto it, **Then** every item on that tile is collected.
3. **Given** an empty tile ahead, **When** the player moves onto it, **Then** the inventory is unchanged.
4. **Given** a tile occupied by an enemy, **When** the player moves into it, **Then** combat occurs, the player does not move, and no item is collected.

---

### User Story 2 - Picking up a better weapon makes the player stronger (Priority: P2)

When a player collects a weapon that is stronger than what they currently wield, it is
equipped automatically and their melee damage increases immediately.

**Why this priority**: This is what makes collecting items *matter* mid-run — it wires
the existing weapon slot and strength attribute into the only live mechanic (combat).

**Independent Test**: With no weapon equipped, pick up a weapon with a strength bonus,
then run a guaranteed-hit strike and confirm the damage includes the weapon bonus.

**Acceptance Scenarios**:

1. **Given** no weapon equipped, **When** the player picks up a weapon with a strength bonus, **Then** that weapon becomes equipped.
2. **Given** an equipped weapon, **When** the player picks up a stronger weapon, **Then** the stronger weapon becomes equipped; **When** they pick up a weaker or non-weapon item, **Then** the equipped weapon is unchanged.
3. **Given** a weapon is equipped, **When** the player lands a hit, **Then** the damage dealt equals base strength plus the weapon's strength bonus.

---

### User Story 3 - Collected items survive save and reload (Priority: P3)

A player who collects items, saves, and later reloads finds their inventory intact and
their equipped weapon still equipped. Items they already collected do not reappear on
the floor.

**Why this priority**: Persistence is required by the project's backward-compatible
persistence principle; without it a reload silently loses progress and respawns loot.

**Independent Test**: Collect an item, save, reload, and verify the inventory and
equipped weapon are restored and the collected item is absent from its original floor.

**Acceptance Scenarios**:

1. **Given** a saved game with a non-empty inventory, **When** it is reloaded, **Then** every collected item and the equipped weapon are restored.
2. **Given** an item was collected before saving, **When** the game is reloaded, **Then** that item does not reappear on the floor it came from.
3. **Given** a save written before this feature existed (no inventory field), **When** it is loaded, **Then** the player starts with an empty inventory and no weapon, and all other state restores correctly.

---

### Edge Cases

- Item and stairs on the same tile → the item is collected before the floor transition.
- Item and enemy on the same tile → combat takes precedence; the player does not enter
  the tile, so the item is not collected until the enemy is defeated.
- A non-weapon item (treasure, consumable, misc) → collected into inventory, never equipped.
- A weapon whose name is not in the item library → collected, but carries no strength
  bonus, so it is never auto-equipped over a real weapon.
- Legacy save with no inventory field → empty inventory, no weapon, loads cleanly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Moving the player onto a tile that holds one or more items MUST add every item on that tile to the player's inventory and remove them from the floor.
- **FR-002**: A collected item MUST no longer be rendered by any visualizer and MUST NOT be collectible a second time.
- **FR-003**: Collecting a weapon whose strength bonus exceeds the currently equipped weapon's MUST auto-equip it; collecting a weaker or non-weapon item MUST leave the equipped weapon unchanged.
- **FR-004**: Melee damage MUST reflect the equipped weapon's strength bonus immediately after it is equipped.
- **FR-005**: Combat MUST take precedence over pickup — moving into an enemy-occupied tile triggers combat, the player does not advance, and no item is collected.
- **FR-006**: The save file MUST record the player's inventory and which item (if any) is equipped as the weapon.
- **FR-007**: Loading a save MUST restore the inventory and the equipped weapon, and MUST NOT respawn any collected item on the floor it was taken from.
- **FR-008**: Saves written before this feature (no inventory field) MUST load without error, yielding an empty inventory and no equipped weapon, with all other state intact.
- **FR-009**: A change to the save format MUST be reflected in a `schema_version` bump (1 → 2), and item-pickup persistence MUST be covered by an automated regression test that loads an older-version save fixture.

### Key Entities

- **Inventory**: the ordered collection of items a player has picked up. Lives on the
  `Player`. Holds item records (name, value, description, category, effect, origin
  position/floor). Persisted in the save file.
- **Equipped Weapon**: a reference to the inventory item currently filling the weapon
  slot, contributing its strength bonus to melee damage. Persisted as a reference into
  the inventory.
- **Save File** (`game_state.json`): now also carries the inventory and equipped-weapon
  reference, and is stamped `schema_version` 2.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of items walked over are collected and removed from the floor in a single step.
- **SC-002**: After picking up a strictly stronger weapon, the next guaranteed hit deals more damage than before — every time.
- **SC-003**: A save → reload round-trip restores inventory and equipped weapon with zero loss and zero respawned loot in 100% of attempts.
- **SC-004**: 100% of pre-feature saves continue to load (no regression in existing load behavior).
- **SC-005**: Automated pickup, auto-equip, and persistence coverage exists and passes in the standard test run.

## Assumptions

- Pickup is automatic on stepping onto the tile (mirrors the existing auto-combat on
  moving into an enemy) — there is no separate "pick up" key.
- "Stronger weapon" is decided solely by the weapon's strength bonus; ties do not
  re-equip.
- Consumable *use* (e.g. drinking a Health Potion), armor/accessory slots, dropping,
  selling, and any inventory HUD/screen are out of scope (separate roadmap items).
- The single-file `game_state.json` is the only save slot in scope.

## Clarifications

### Session 2026-06-19

- Q: How far should pickup go? → A: Pickup into inventory **plus** auto-equip weapons; consumable use is out of scope.
- Q: Should the inventory persist across save/load? → A: Yes — persist it and bump `schema_version` 1 → 2 with a save regression test.
