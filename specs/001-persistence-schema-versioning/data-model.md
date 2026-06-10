# Data Model: Persistence Schema Versioning

**Date**: 2026-06-10 | **Plan**: [plan.md](plan.md)

---

## Save File Schema

Single file: `game_state.json` (path held in `STATE_FILE` in `game_state.py`).

### Schema v1 (new — written by this feature)

```json
{
  "schema_version": 1,
  "dungeon": "DebugMapLoader.dngn",
  "floor": 0,
  "x": 1,
  "y": 1,
  "facing": "north",
  "hp": 10,
  "mp": 1,
  "attack": 0.5,
  "strength": 1,
  "defense": 1,
  "max_hp": 10,
  "intelligence": 1,
  "mana": 1,
  "xp": 0,
  "level": 1,
  "enemies": [
    {
      "name": "Rat",
      "hp": 5,
      "attack": 2,
      "speed": 1,
      "grid_x": 3,
      "grid_y": 4,
      "xp": 5
    }
  ]
}
```

### Schema v0 (legacy — no version field)

Identical to v1 except `schema_version` is absent. All existing saves on disk are v0.
`from_save()` reads `data.get("schema_version", 0)` → 0, and proceeds normally.

```json
{
  "dungeon": "DebugMapLoader.dngn",
  "floor": 0,
  "x": 1,
  "y": 1,
  "facing": "north",
  "hp": 10,
  "mp": 1,
  "attack": 0.5,
  "strength": 1,
  "defense": 1,
  "max_hp": 10,
  "intelligence": 1,
  "mana": 1,
  "xp": 0,
  "level": 1,
  "enemies": []
}
```

This v0 snapshot (with `"enemies": []`) is also the content of the test fixture at
`tests/fixtures/legacy_save_v0.json`.

---

## Field Reference

| Field | Type | Access in from_save() | Default (if absent) |
|-------|----|----------------------|---------------------|
| `schema_version` | `int` | `.get("schema_version", 0)` | 0 (legacy) |
| `dungeon` | `str` | `data["dungeon"]` | — (required) |
| `floor` | `int` | `data["floor"]` | — (required) |
| `x` | `int` | `data["x"]` | — (required) |
| `y` | `int` | `data["y"]` | — (required) |
| `facing` | `str` | `data["facing"]` | — (required) |
| `hp` | `int` | `data["hp"]` | — (required) |
| `mp` | `int` | `data["mp"]` | — (required) |
| `attack` | `float` | `.get("attack", 0.5)` | 0.5 |
| `strength` | `int` | `.get("strength", 1)` | 1 |
| `defense` | `int` | `.get("defense", 1)` | 1 |
| `max_hp` | `int` | `.get("max_hp", 10)` | 10 |
| `intelligence` | `int` | `.get("intelligence", 1)` | 1 |
| `mana` | `int` | `.get("mana", 1)` | 1 |
| `xp` | `int` | `.get("xp", 0)` | 0 |
| `level` | `int` | `.get("level", 1)` | 1 |
| `enemies` | `list` | `data["enemies"]` | — (required) |
| `enemies[].name` | `str` | `e["name"]` | — (required) |
| `enemies[].hp` | `int` | `e["hp"]` | — (required) |
| `enemies[].attack` | `int` | `e["attack"]` | — (required) |
| `enemies[].speed` | `int` | `e["speed"]` | — (required) |
| `enemies[].grid_x` | `int` | `e["grid_x"]` | — (required) |
| `enemies[].grid_y` | `int` | `e["grid_y"]` | — (required) |
| `enemies[].xp` | `int` | `.get("xp", 0)` | 0 |

---

## Version Compatibility Matrix

| Save version | Supported? | Load behaviour |
|---|---|---|
| absent (v0) | Yes | `schema_version` defaults to 0; loads with existing defaults |
| 1 | Yes | Loads normally |
| > 1 | No | `ValueError` raised; file untouched |
| corrupt/non-integer | No | `ValueError` raised (Python will raise on `>` comparison if not int) |

---

## Constant

```python
SCHEMA_VERSION: int = 1  # bump when persisted fields change
```

Defined at module level in `game_state.py`. Bump this value whenever the set of
persisted fields changes or the load logic must behave differently for new saves.
