# ToME 2 Map Generation

A reference summary of how *ToME 2* (Tales of Middle-earth / Troubles of Middle-earth)
generates its world, kept alongside the [Rogue](rogue-map-generation-plan.md),
[SPD](SPD-map-generation-plan.md), [NetHack](nethack-map-generation-plan.md),
[Angband](angband-map-generation-plan.md), [DCSS](DCSS-map-generation-plan.md), and
[Brogue](brogue-map-generation-plan.md) plans for comparison.

ToME 2 is an **Angband variant**, so its dungeon generator *is* the Angband
rooms-tunnels-vaults pipeline (`generate.c`): a block grid filled with granite, rooms drawn
from templates and placed into free blocks, room centers joined by bending `build_tunnel`
corridors, then streamers, doors, stairs, monsters, and objects — see the
[Angband summary](angband-map-generation-plan.md) for that core. This document focuses on
what ToME 2 **adds on top**.

## Per-dungeon generation flags (the main lever)

ToME 2's defining change is that each dungeon is described by a **data file** (`d_info.txt`)
carrying a set of **generation flags** (`DF_*`) that reshape the Angband generator for that
place. So Barrow-downs, Mirkwood, Moria, Mordor, and Angband all run *the same* generator
tuned differently. Representative flags:

- **Shape/style:** `DF_CAVERN` (cellular/fractal caves instead of rooms), `DF_MAZE` (maze
  levels), `DF_EMPTY` (open "arena" levels), `DF_CIRCULAR_ROOMS`, `DF_FLAT`.
- **Size:** `DF_SMALL_LEVELS` / `DF_BIG` — levels can be generated at a fraction of full
  size (any level also has a random chance of being "small").
- **Direction:** `DF_TOWER` — a tower you ascend rather than descend; `DF_NO_UP` /
  `DF_NO_DOWN` constrain stairs.
- **Terrain:** `DF_WATER_RIVER` / `DF_LAVA_RIVER` carve **rivers** across the level;
  `DF_NO_DOORS`, `DF_ADJUST_LEVEL_*` (out-of-depth tuning), and more.

This flag system is why ToME 2 dungeons feel distinct without a separate generator per
dungeon — it's Angband's pipeline, parameterized.

## The wilderness overworld

Above the dungeons sits a **wilderness map**: a grid of terrain tiles (forest, mountains,
plains, water…) defined from wilderness feature data (`wf_info.txt`) plus a world layout.
**Towns** and **dungeon entrances** live at fixed wilderness locations. Each wilderness tile
can be entered and is generated as a small overworld level from its terrain type, so travel
happens on the map and dungeons hang off it — a structural layer neither Rogue nor Angband's
base game has.

## Rivers, vaults, and special levels

- **Rivers** of water or lava (per the `DF_*_RIVER` flags) snake across a level, on top of
  the usual magma/quartz streamers.
- **Vaults** come from ToME's `v_info.txt` templates — lesser/greater vaults and nests/pits,
  placed rarely, as in Angband.
- **Quest and unique levels** (and some **persistent** dungeon levels that stay as you left
  them) are fixed or specially generated rather than fully random.

## What's distinctive

ToME 2 keeps Angband's **rooms-tunnels-vaults core** but wraps it in two big ideas: a
**wilderness overworld** that ties dungeons together, and a **per-dungeon flag system** that
re-skins the same generator into caves, mazes, towers, river-cut levels, and more. It's the
"one parameterized generator, many dungeons" approach — contrast DCSS's per-branch vault
libraries or NetHack's genuinely separate generators.
