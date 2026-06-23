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
