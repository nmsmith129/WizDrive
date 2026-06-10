# Quickstart: Testing Persistence Schema Versioning

**Date**: 2026-06-10 | **Plan**: [plan.md](plan.md)

---

## Run the full test suite

```powershell
python -m pytest tests/ -v
```

All 18 existing tests plus the 4 new schema-version tests must pass.

---

## Verify a new save carries `schema_version`

```powershell
python -c "
import wiz_drive_main  # or however the game initialises state
# Alternatively, load a map and save directly:
from map_loader import load_map_file
from game_state import GameState
_, _, floors = load_map_file('DebugMapLoader.dngn')
from player import Player
p = Player('Hero')
gs = GameState('DebugMapLoader.dngn', floors, 0, p, [])
gs.save()
import json, pathlib
data = json.loads(pathlib.Path('game_state.json').read_text())
print('schema_version:', data.get('schema_version'))  # expect: 1
"
```

---

## Simulate loading a legacy (v0) save

```powershell
python -c "
import json, pathlib, pygame
pygame.init()
# Write a legacy save (no schema_version)
legacy = {
    'dungeon': 'DebugMapLoader.dngn',
    'floor': 0, 'x': 1, 'y': 1, 'facing': 'north',
    'hp': 10, 'mp': 1, 'enemies': []
}
pathlib.Path('game_state.json').write_text(json.dumps(legacy))
from game_state import GameState
gs = GameState.from_save()
print('Loaded OK. Player HP:', gs.player.hp)  # expect: 10
"
```

---

## Simulate a newer-version save (expect rejection)

```powershell
python -c "
import json, pathlib, pygame
pygame.init()
future_save = {
    'schema_version': 99,
    'dungeon': 'DebugMapLoader.dngn',
    'floor': 0, 'x': 1, 'y': 1, 'facing': 'north',
    'hp': 10, 'mp': 1, 'enemies': []
}
pathlib.Path('game_state.json').write_text(json.dumps(future_save))
from game_state import GameState
try:
    gs = GameState.from_save()
    print('ERROR: should have raised ValueError')
except ValueError as e:
    print('Correctly rejected:', e)
"
```

---

## Test fixture location

`tests/fixtures/legacy_save_v0.json` — committed static file used by
`test_legacy_v0_save_loads`. Content matches schema v0 (no `schema_version` field),
references `DebugMapLoader.dngn`.
