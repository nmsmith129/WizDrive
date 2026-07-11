# Brogue Map Generation

A reference summary of how *Brogue* generates its levels (`Architect.c`), kept alongside the
[Rogue](rogue-map-generation-plan.md) and [SPD](SPD-map-generation-plan.md) plans for
comparison. Brogue is the **modern classic** whose levels feel hand-designed while being
fully procedural — the closest lineage to what WizDrive targets, and a heavy user of the
same **Dijkstra distance-map** technique WizDrive's `Pathfinding` already implements.

## Room accretion

1. **Attach rooms one at a time.** Start with a single room, then repeatedly generate a
   **candidate room** and try to **attach** it to the existing dungeon where one of its
   doorways lines up against an existing wall, rejecting the candidate if its footprint
   overlaps. Because every room joins through a door, **connectivity is guaranteed by
   construction** — no flood-fill rejection needed for basic reachability.
2. **Varied room shapes.** Candidates are drawn by frequency from a set of procedural
   shapes: **cross rooms, circular rooms, small symmetric rooms, big rooms**, and **cave
   rooms** grown by cellular-automata blobs.

## Loops, terrain, and machines

3. **Add loops.** The accretion produces a tree (one path between any two points), so
   `addLoops` punches **extra passages through thin walls** — specifically where two floor
   tiles are close in space but *far apart along existing corridors* (measured with a
   distance map). This creates cycles and alternate routes without random clutter.
4. **Lakes and chasms.** `designLakes` floods blob-shaped **water/lava lakes** and adds
   chasms, layering terrain over the room structure.
5. **Machines — the signature feature.** `buildAMachine` places designed set-pieces:
   **reward vaults, guardian puzzles, captive monsters, and key-and-door / commutation
   puzzles**. Machines use **flow (Dijkstra) maps** over the level to guarantee they are
   solvable and to shape how the player must move through them.

## Dijkstra flow maps everywhere

Brogue leans on distance maps throughout: to verify connectivity, to place the two staircases
**far apart**, to drive monster and item flow, and as the backbone of machine logic. This is
the exact "Brogue Dijkstra map" idea documented for WizDrive's `Pathfinding`.

## What's distinctive

**Accretion + loop-adding + flow-driven machines** yield levels that read as *designed* yet
are entirely generated. Where DCSS authors set-pieces by hand, Brogue *procedurally
constructs* them under connectivity and flow constraints — the most relevant model for a
Brogue-lineage roguelike like WizDrive.
