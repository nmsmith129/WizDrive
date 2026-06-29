# WizDrive — Code Review Notes

Running log of findings from the manual source review. Each entry records the
file/line, the observation, its impact, a suggested fix, and a status.

## Decided Refactor — Event-driven combat

> Consolidates several individual findings below into one coherent piece of
> work. The entries it subsumes are kept in place (not deleted) and marked
> **Subsumed by:** this section.

- **Decision:** Restructure combat around a one-directional, event-driven design
  with `GameState` as the turn coordinator. Game pieces (`Player`, `Enemy`) never
  reach into `GameState`; instead the coordinator *asks* them to act and they
  *report* what happened by returning (or appending to an injected sink) plain
  event records. This keeps the dependency graph acyclic (`GameState → Player/
  Enemy`, never back) and avoids the circular-import trap entirely.
- **Why this is one change, not several:** the event-return pattern is the shared
  mechanism that makes each of the subsumed findings fall out naturally —
  splitting `strike()`, adding `do_combat()`, removing `print` from the models,
  and renaming `attack → accuracy` can all land in the same pass.
- **Shape:**
  - `Player`: pure attack method (roll + damage, returns a result/events; no
    counter-attack, no `print`) + `gain_xp(n)` handling level-ups.
  - `Enemy`: its own `act(player) -> list[event]` (or an injected `post_event`
    callback); no `game_state` import — uses duck-typed objects passed in.
  - `GameState.do_combat()`: runs *player phase → resolve → enemy phase →
    resolve*, aggregates events into a single list it owns, removes the dead,
    awards XP.
  - Visualizers: render the collected events instead of entities printing.
- **Bundled cleanups:** rename `Player.attack → accuracy`/`hit_chance` (needs a
  save-schema/migration thought so old saves keep loading); reconcile CLAUDE.md's
  documented `GameState._do_combat()` with the chosen `do_combat()` name.
- **Sequencing:** finish the manual read-through first — the visualizers and
  entry point are the event *consumers*, and how they render combat should shape
  the event schema before it's fixed.
- **Subsumes:** "player.py — `strike()` fuses both halves of a combat round",
  "player.py — `attack` attribute is misnamed", and "game_state.py — combat
  should be extracted into a `do_combat()` method" (all below).
- **Status:** Decided; not yet started. Plan to be written before implementation.

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
- **Subsumed by:** "Decided Refactor — Event-driven combat" (top of file).
- **Status:** Subsumed.

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

### player.py — `attack` attribute is misnamed (it's accuracy, not damage)
- **Files:** src/wiz_drive/player.py:19 (`self.attack`), used at :74
  (`random.random() < self.attack`); contrast enemy.py:15 (`enemy.attack`).
- **Finding:** `Player.attack` is a *to-hit probability* (`float`, default 0.5 =
  50% hit chance), but the name reads like a damage/offense stat. Actual damage
  is `strength + weapon.strength`. Worse, the same attribute name means
  something different on the Enemy: `Enemy.attack` is a flat *damage* value
  (`int`), used as `max(1, enemy.attack - self.defense)` in the counter-attack.
  So `attack` = hit chance on Player but = damage on Enemy.
- **Impact:** Genuinely misleading — easy to read `player.attack` as damage and
  misunderstand the combat math (this tripped up the review). The cross-class
  name collision compounds it.
- **Suggested fix:** Rename `Player.attack` to `accuracy` (or `hit_chance`).
  Touches: Player.__init__ param + attribute, the `strike()` roll, the
  save/load round-trip in game_state.py (`data.get("attack", 0.5)` key and the
  `save()` dict — needs a schema/migration thought so old saves still load),
  and any tests referencing `player.attack`. Consider doing it alongside the
  `strike()` combat refactor above.
- **Subsumed by:** "Decided Refactor — Event-driven combat" (top of file);
  bundled in as the `attack → accuracy` rename.
- **Status:** Subsumed (rename agreed).

### game_state.py — combat should be extracted into a `do_combat()` method
- **Files:** src/wiz_drive/game_state.py:124-126 (combat handled inline in
  `apply_key`).
- **Finding:** Combat resolution is currently inlined in `apply_key` — on a move
  into an occupied tile it calls `self.player.strike(target)` directly and
  removes the enemy on a kill. There is no dedicated combat method on
  `GameState`. (Note: CLAUDE.md already documents a `GameState._do_combat()` as
  if it exists, but it does not — the docs are ahead of the code.)
- **Recommendation:** Extract combat into its own method, **`do_combat()`**, so
  `apply_key` just dispatches to it and the combat logic has a clear home. This
  is the natural seat for the turn-coordinator role described in the `strike()`
  refactor note above (run player phase → resolve → enemy phase → render).
- **Scope:** game_state.py; ties directly into the `strike()` combat refactor.
  Also reconcile CLAUDE.md (`_do_combat` vs `do_combat`) once the method exists.
- **Subsumed by:** "Decided Refactor — Event-driven combat" (top of file).
- **Status:** Subsumed.

### Map is loaded multiple times instead of loaded once and shared
- **Files:** `load_map_file` call sites — src/wiz_drive/wiz_drive_main.py:128,
  src/wiz_drive/game_state.py:58 (`from_save`), src/wiz_drive/test_visualizer.py:29,
  src/wiz_drive/text_visualizer.py:68 & 85, plus map_loader.py:614 (loader CLI).
- **Finding:** Each entry point / tool calls `load_map_file` independently. The
  game itself loads in two different places (fresh start in `main`, save path in
  `GameState.from_save`), and the standalone viewers each load their own copy.
  The same parse work and call pattern (`_, _, floors = load_map_file(path)`) is
  duplicated across modules.
- **Decision (owner):** Load the map **once** and pass the loaded data
  (`floors` / a shared state object) around between modules, rather than having
  each module load it independently. Aim is a single load point with the result
  shared — eliminating the duplicated `load_map_file` calls. The owner framed
  this as deliberately increasing integration/coupling between modules around one
  shared loaded map (accepting that the standalone viewers become dependent on
  that shared load path rather than loading independently).
- **Scope:** wiz_drive_main.py (becomes/feeds the single load point), game_state.py
  (make `new` symmetric with `from_save` re: who loads), and both visualizers
  (`run_debug_viewer` / text render take pre-loaded data instead of a path, or
  receive a shared state object).
- **Note / tension:** This is the opposite direction from the data-model
  *decoupling* notes above (pygame-free entities, event-driven combat). Those
  reduce coupling between *layers*; this centralizes *map loading* so it happens
  once. Not contradictory, but worth designing deliberately so the shared load
  point doesn't drag the full game/save machinery into the read-only viewers.
- **Status:** Decided; not yet started.

### first_person.py — review skipped; candidate for deletion
- **Files:** src/wiz_drive/first_person.py (not yet reviewed).
- **Note:** Owner is intentionally skipping the manual review of this file for now
  and may delete it entirely later.
- **If deleted, also touches:**
  - src/wiz_drive/wiz_drive_main.py — the `VISUALIZER == 2` branch
    (lines 20-21 conditional import of `FirstPersonVisualizer`, `run_first_person`
    at :62, and dispatch at :135-136) would need removing.
  - first_person_test.txt — manual first-person sanity-check checklist becomes
    obsolete.
- **Status:** Review deferred; possible removal pending owner decision.
