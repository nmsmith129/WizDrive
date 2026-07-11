# Angband Map Generation

A reference summary of how *Angband* generates its dungeon levels (`generate.c` and the
room-template / vault system), kept alongside the [Rogue](rogue-map-generation-plan.md) and
[SPD](SPD-map-generation-plan.md) plans for comparison. Angband levels are **large and
scrollable** (many screens wide/tall), built from a big catalog of room templates plus
hand-designed vaults, wired together by tunnels.

## Blocks and dungeon profiles

1. **A grid of blocks.** The level is divided into fixed-size **blocks** (~11×11 tiles). The
   generator tracks which blocks are occupied so rooms don't collide, and places rooms into
   free blocks.
2. **A dungeon profile chooses the style.** Each level picks a profile —
   *modified/classic*, *cavern*, *labyrinth*, *moria*, *lair*, etc. — that decides the
   overall look and which room types are eligible at the current depth.

## Rooms, tunnels, and terrain (the default profiles)

3. **Rooms from templates.** A large set of room types, each with a **rarity and depth
   requirement**: simple rooms, overlapping and cross rooms, large/pillared rooms, monster
   **nests** and **pits**, and **lesser/greater vaults** — ASCII templates loaded from data
   files, placed rarely, packed with tough monsters and good loot.
4. **Tunnels connect rooms.** `build_tunnel()` links room centers with a **semi-random,
   bending path** that occasionally pierces walls; doors are placed at junctions.
5. **Streamers and clutter.** `build_streamer()` cuts **magma/quartz veins** diagonally
   across the whole level, some bearing treasure; rubble, traps, and doors are scattered in.

## Alternate profiles

*Cavern* levels use **cellular automata** for organic caves, *labyrinth* levels are
**mazes**, and *moria* levels mimic the older Moria style — each replacing the
rooms-and-tunnels step wholesale.

## Validation and population

The level's **connectivity is checked** (flood fill from the stairs); if regions are
stranded the builder patches with tunnels or regenerates. Then stairs, depth-scaled (and
occasionally out-of-depth) monsters, and objects are placed.

## What's distinctive

Angband is **template-and-vault driven** at large scale: dozens of room archetypes and
data-file vaults, big scrollable maps, and a **profile system** that can swap the entire
generation style per level. The flood-fill connectivity backstop mirrors what WizDrive does
with `dijkstra_map_4`.
