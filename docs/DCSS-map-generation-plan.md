# Dungeon Crawl Stone Soup Map Generation

A reference summary of how *Dungeon Crawl Stone Soup* generates levels (`dungeon.cc` plus
the `.des` / Lua **map** system), kept alongside the [Rogue](rogue-map-generation-plan.md)
and [SPD](SPD-map-generation-plan.md) plans for comparison. DCSS is the most
**vault-driven** of the classics: nearly every structure — and often the entire floor — is
a "map" (vault) authored in `.des` files, combined with procedural layouts and rigorously
validated for connectivity.

## Everything is a map (vault)

1. **`.des` maps, tiny to whole-floor.** A map ranges from a small **minivault** to a
   full-level **layout**. Each has a header (`TAGS`, `DEPTH`, `ORIENT`, `WEIGHT`, and
   glyph→feature/monster/item definitions like `KFEAT`/`KMONS`/`KITEM`) and an ASCII
   **`MAP`** block. Markers — `SUBST`, `SHUFFLE`, `NSUBST`, and embedded **Lua** — randomize
   contents so the same map plays differently each time.

## Build order

2. **Layout first.** The builder picks a **primary layout** that fills the floor. Layouts
   may be procedural (random rooms + corridors, cellular-automata caves, "city" of
   rectangular rooms, water/island layouts) or a **branch-specific** map.
3. **Then place vaults.** **Mandatory** vaults (stair vaults, branch entries, unique
   features) are placed first, then a **random selection** of encounter and decorative
   minivaults, all respecting tags and depth.

## Connectivity and vetoes

4. **Strict reachability.** All stairs and key features must be connected. A placement that
   breaks connectivity is **rejected and retried**, and a level that can't be made valid is
   **regenerated** — DCSS's "veto" system. This is the primary correctness guarantee, much
   stronger than a post-hoc flood check.

## Branch flavor

Each branch carries its own layouts and vault pool — **Lair** caves, **Shoals** islands and
water (noise-driven), **Swamp**, **Crypt**, the vault-heavy **Vaults** branch, **Slime**,
and more — so the generator's output varies dramatically by where you are.

## What's distinctive

DCSS is a **hybrid**: procedural base layouts seeded with a deep library of **hand-authored,
Lua-scriptable vaults**, everything gated by a **connectivity veto**. It is the far end of
the "author the interesting bits, generate the glue" spectrum — contrast Rogue, which is
almost purely procedural.
