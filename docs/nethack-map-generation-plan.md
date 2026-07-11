# NetHack Map Generation

A reference summary of how *NetHack* generates its levels (`mklev.c`, `mkroom.c`,
`mkmaze.c`, `sp_lev.c`), kept alongside the [Rogue](rogue-map-generation-plan.md) and
[SPD](SPD-map-generation-plan.md) plans for comparison. NetHack descends directly from
Rogue's rooms-and-corridors, but layers on special rooms, a large body of hand-authored
levels, and entirely separate cave/maze generators for different branches. It is
**heterogeneous**: which generator runs depends on depth and branch.

## Rooms and corridors (the main dungeon)

1. **Place rooms freely.** `makerooms()` repeatedly calls `create_room()` to drop rooms at
   **random positions and sizes**, rejecting any that overlap an existing room (plus a
   margin). Unlike Rogue, rooms are **not** confined to a 3×3 grid — placement continues
   until the level is full, a room cap is hit, or a random early stop. Rooms are marked
   lit or dark, and are usually rectangular (occasionally other shapes).
2. **Connect with corridors.** `makecorridors()` joins rooms in index order (room *i* to
   *i+1*) and then adds a few extra random links. `join()` digs a **bending corridor** that
   navigates around existing rooms; corridors may cross one another, and a **door** is cut
   where a corridor meets a room wall. The index-order joins guarantee the level is
   connected.
3. **Designate special rooms.** After placement, some rooms become **shops, vaults,
   temples, thrones, zoos, beehives, barracks, morgues**, etc., each with themed contents
   and monsters.

## Hand-authored special levels

A large fraction of the game is **not** procedural. NetHack ships a **level compiler** that
turns `.des` description files into fixed or semi-fixed levels: the Oracle, Big Room,
Sokoban, Mines' End, the Castle, Vlad's Tower, the quest levels, and the endgame planes.
A `.des` file combines ASCII **`MAP`** blocks with placement directives (monsters, objects,
traps, regions) and randomization markers, so a "fixed" level can still vary its contents.

## Alternate generators by branch

- **Gnomish Mines** use a **cellular-automata cave generator** (`mkmap()`), producing
  organic blob caverns instead of rooms-and-corridors.
- **Gehennom and other maze levels** use a **randomized maze carver** (`makemaz()` /
  `walkfrom`) over the whole grid.

## What's distinctive

NetHack's signature is **variety by location**: a Rogue-style room generator for the upper
dungeon, CA caves for the Mines, mazes for Gehennom, and a deep catalog of hand-designed
set-piece levels — all selected by depth and branch. Connectivity in the room generator is
structural (index-order joins), the same idea WizDrive's spanning tree uses.
