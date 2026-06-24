# WizDrive — Code Review Notes

Running log of findings from the manual source review. Each entry records the
file/line, the observation, its impact, a suggested fix, and a status.

## Code Review Notes

### enemy.py / item.py — vestigial pygame sprite state
- **Files:** src/wiz_drive/enemy.py:20-22, src/wiz_drive/item.py:21-23
- **Finding:** `self.image` (pygame.Surface) and `self.rect` are built in every
  Enemy/Item constructor but never used for rendering. The pygame visualizer
  computes its own pixel positions via `_to_screen` and draws with
  `pygame.draw.rect` + its own colors; it never reads `.image`/`.rect`. Only
  references are debug prints in map_loader.py:162-163, 218-219.
- **Impact:** Forces `pygame.init()` as a hard precondition even for headless
  text/test runs; couples the data models to pygame for no benefit.
- **Suggested fix (later):** Drop `image`/`rect`; keep `grid_x/grid_y`. Makes
  Enemy/Item pure data models, decoupling them from pygame.
- **Status:** Partially resolved.
  - `self.rect` **removed** from both `Enemy` and `Item`; the corresponding
    `.rect` debug prints in map_loader.py (formerly lines 163 and 219) were
    deleted.
  - `self.image` **retained** but repurposed: both constructors now accept an
    optional `loaded_image: pygame.Surface | None` that is scaled to
    `TILE_SIZE`, falling back to the solid-color placeholder when `None`. So
    `image` is no longer dead state, but it still keeps the data models coupled
    to pygame (and `pygame.init()` a precondition). Full decoupling — e.g.
    moving art loading into the visualizer — remains open.

### player.py — `strike()` fuses both halves of a combat round
- **Files:** src/wiz_drive/player.py:71-95 (`Player.strike`); call site
  src/wiz_drive/game_state.py:124-126.
- **Finding:** `strike()` is named like a single player action but actually runs
  an entire combat exchange: (1) player hit roll + damage, (2) enemy death
  detection, (3) XP award, (4) level-up, (5) the **enemy's counter-attack**,
  (6) player damage/death, (7) all narration via `print`. The enemy's turn is
  hardcoded inside the player's method.
- **Impact:** There is no real enemy phase. The only enemy that ever acts is the
  single one the player walks into, and it only ever counter-attacks once. The
  design cannot express "each enemy takes a turn" (e.g. a second adjacent enemy
  never acts). Also mixes player progression, enemy behavior, and presentation
  in one method.
- **Suggested fix (later):** Restructure as a turn/round loop —
  *player phase → resolve → enemy phase → resolve → render*:
  - `Player`: pure attack method (roll + damage to a target, returns a result;
    no counter-attack, no print) + a `gain_xp(n)` that handles leveling.
  - `Enemy`: its own turn method (e.g. `act(player)` / `take_turn`).
  - `GameState`: turn coordinator — runs the phases, awards XP on kill, removes
    the dead, iterates living enemies.
  - Visualizer/UI: render combat events instead of `strike()` printing them
    (same presentation-coupling theme as the entry above).
- **Scope:** Touches Player, Enemy, GameState, both visualizers, and the
  `strike()`-based assertions in tests/test_combat.py.
- **Status:** Observed, not yet decided.

### map_loader.py — large `if debug:` instrumentation block, dead in gameplay
- **Files:** src/wiz_drive/map_loader.py — 44 `if debug:` sites throughout.
- **Finding:** Every parse/validate helper is wrapped in verbose `if debug:`
  diagnostic prints. With the module-level `debug = False` default (and every
  entry point keeping it false per CLAUDE.md), none of this runs during normal
  gameplay or tests — it only executes when the module is run standalone
  (`python -m wiz_drive.map_loader`).
- **Impact:** Not a bug, but it is the bulk of the file's line count and noise.
  It obscures the actual parsing logic when reading, and the prints duplicate
  state already visible in a debugger. Inert in production by design.
- **Suggested fix (later):** Thin it out — keep a few high-value traces, drop
  the line-by-line dumps; or replace the `debug` bool + prints with the stdlib
  `logging` module so verbosity is controlled per-run without dead branches.
- **Status:** Observed, not yet decided.

### map_loader.py — explicit-stats ENEMY still does a library lookup for `xp`
- **Files:** src/wiz_drive/map_loader.py:142 (`_parse_enemy_line`, 6-field
  branch); `get_stats` fallback in src/wiz_drive/enemy.py.
- **Finding:** The 6-field `ENEMY|name|hp|attack|speed|x y` form takes hp/attack/
  speed from the line but still calls `get_stats(name)` solely to obtain `xp`
  (xp is intentionally not part of the map format — see CLAUDE.md). This is one
  lookup, not a redundant double-call; the notable part is the *behavior*: for a
  name absent from `ENEMY_TYPES`, `get_stats` silently returns the fallback
  `xp: 0`. So a fully-explicit enemy with an unrecognized name parses fine but
  is worth 0 XP with no warning.
- **Impact:** Minor/by-design, but a quietly surprising edge: explicit stats
  imply "I don't need the library," yet xp still depends on it, and an unknown
  name degrades to 0 xp instead of erroring or warning.
- **Suggested fix (later):** Either (a) allow an optional 7th xp field on the
  explicit form, or (b) emit a warning when an explicit-stats enemy's name is
  not in `ENEMY_TYPES` so the silent xp=0 is visible.
- **Status:** Observed, not yet decided.
