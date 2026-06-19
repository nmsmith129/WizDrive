"""
Tests for the Item Pickup Mechanics feature (spec: specs/002-item-pickup-mechanics/spec.md).

Tasks covered: T003–T006 (US1), T009–T011 (US2), T014–T018 (US3).

All tests target the UNIMPLEMENTED state — they are expected to FAIL until
the feature is implemented (Constitution Principle I: Test-First).
"""
from __future__ import annotations

import json
import pathlib

import pytest

import game_state as gs
import player as player_module
from game_state import GameState
from player import Player
from item import Item
from enemy import Enemy

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_player(hp: int = 20, location: tuple = (5, 5), facing: str = "north") -> Player:
    p = Player("Hero", hp=hp)
    p.location = location
    p.facing = facing
    return p


def _make_item(name: str = "Gold Coin", value: int = 5, description: str = "Shiny",
               grid_x: int = 5, grid_y: int = 6,
               category: str = "misc", effect: dict | None = None) -> Item:
    return Item(name, value, description, grid_x, grid_y,
                category=category, effect=effect or {})


def _make_weapon(name: str = "Iron Sword", strength: int = 4,
                 grid_x: int = 5, grid_y: int = 6) -> Item:
    return Item(name, 30, "A sturdy blade", grid_x, grid_y,
                category="weapon", effect={"strength": strength})


def _make_enemy(name: str = "Goblin", hp: int = 30, attack: int = 3,
                grid_x: int = 5, grid_y: int = 6) -> Enemy:
    return Enemy(name, hp=hp, attack=attack, speed=1, grid_x=grid_x, grid_y=grid_y)


def _make_state(player: Player, enemies: list, items: list,
                grid: list | None = None) -> GameState:
    """
    Builds a GameState with a single 10x10 open floor.
    Player location and item positions must already be set on the objects.
    """
    if grid is None:
        grid = [[0] * 10 for _ in range(10)]
    floor_data = (grid, player.location, player.facing, list(enemies), list(items), None)
    return GameState("dummy.dngn", [floor_data], 0, player, list(enemies))


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures for persistence tests (US3)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def state_file(tmp_path, monkeypatch):
    """Monkeypatches STATE_FILE to a temp path and returns it."""
    path = str(tmp_path / "game_state.json")
    monkeypatch.setattr(gs, "STATE_FILE", path)
    return path


@pytest.fixture
def always_hit(monkeypatch):
    """Forces every strike's hit roll to succeed."""
    monkeypatch.setattr(player_module.random, "random", lambda: 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# User Story 1 — Collect items by walking onto them
# ─────────────────────────────────────────────────────────────────────────────

class TestPickupBasics:
    """T003–T006: core item collection via movement."""

    def test_t003_single_item_collected_and_removed(self):
        """T003: stepping onto a tile with one item adds it to inventory and clears the floor."""
        player = _make_player(location=(5, 5), facing="north")
        coin = _make_item(grid_x=5, grid_y=6)  # one step north of player
        state = _make_state(player, enemies=[], items=[coin])

        # Pre-condition: item on the floor, inventory empty
        assert coin in state.items
        assert not hasattr(player, "inventory") or player.inventory == []

        state.apply_key("w")  # move north onto (5, 6)

        # Post-condition: inventory has the coin, floor is clear
        assert player.location == (5, 6), "Player should have moved"
        assert hasattr(player, "inventory"), "Player must have an inventory attribute"
        assert coin in player.inventory, "Coin should be in player inventory"
        assert coin not in state.items, "Coin should be removed from the floor"

    def test_t004_multiple_items_all_collected_in_one_step(self):
        """T004: two items on the same tile are both collected in a single move."""
        player = _make_player(location=(5, 5), facing="north")
        coin = _make_item("Gold Coin", 5, "Coin", grid_x=5, grid_y=6)
        scroll = _make_item("Ancient Scroll", 50, "Scroll", grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[], items=[coin, scroll])

        state.apply_key("w")

        assert player.location == (5, 6), "Player should have moved"
        assert hasattr(player, "inventory"), "Player must have an inventory attribute"
        assert coin in player.inventory, "Coin should be in player inventory"
        assert scroll in player.inventory, "Scroll should be in player inventory"
        assert len([i for i in state.items if (i.grid_x, i.grid_y) == (5, 6)]) == 0, \
            "No items should remain at (5,6)"

    def test_t005_empty_tile_does_not_change_inventory(self):
        """T005: stepping onto an empty tile leaves player.inventory unchanged."""
        player = _make_player(location=(5, 5), facing="north")
        state = _make_state(player, enemies=[], items=[])

        state.apply_key("w")

        assert player.location == (5, 6), "Player should have moved"
        if hasattr(player, "inventory"):
            assert player.inventory == [], "Inventory should remain empty"

    def test_t006_enemy_and_item_same_tile_combat_no_pickup(self):
        """T006: moving into a tile with both an enemy and an item triggers combat,
        the player does NOT advance, and the item is NOT collected."""
        player = _make_player(location=(5, 5), facing="north")
        # High-hp enemy so combat doesn't kill it in one strike
        goblin = _make_enemy(hp=100, attack=1, grid_x=5, grid_y=6)
        coin = _make_item(grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[goblin], items=[coin])

        state.apply_key("w")

        # Player must NOT have moved into the enemy tile
        assert player.location == (5, 5), "Player should not have moved (blocked by combat)"
        # Item must still be on the floor
        assert coin in state.items, "Item should remain on floor when combat occurs"
        if hasattr(player, "inventory"):
            assert coin not in player.inventory, "Item must NOT be in inventory after blocked combat"


# ─────────────────────────────────────────────────────────────────────────────
# User Story 2 — Auto-equip stronger weapons
# ─────────────────────────────────────────────────────────────────────────────

class TestAutoEquip:
    """T009–T011: Item.strength property, auto-equip logic, and combat bonus."""

    def test_t009_item_strength_returns_effect_strength(self):
        """T009: Item.strength returns effect["strength"] for a weapon and 0 when absent."""
        sword = _make_weapon("Iron Sword", strength=4)
        coin = _make_item("Gold Coin", 5, "Coin", category="treasure")

        assert hasattr(sword, "strength"), "Item must have a 'strength' property"
        assert sword.strength == 4, "Weapon strength should equal effect['strength']"
        assert coin.strength == 0, "Non-weapon item strength should be 0"

    def test_t009_item_without_strength_key_returns_zero(self):
        """T009 (edge): an item with an effect dict but no 'strength' key returns 0."""
        potion = Item("Health Potion", 20, "Heals HP", 0, 0,
                      category="consumable", effect={"heal": 15})

        assert hasattr(potion, "strength"), "Item must have a 'strength' property"
        assert potion.strength == 0, "Potion strength should be 0"

    def test_t010_first_weapon_auto_equipped(self):
        """T010: picking up a weapon sets player.weapon when none is equipped."""
        player = _make_player(location=(5, 5), facing="north")
        assert player.weapon is None, "Player starts with no weapon"

        sword = _make_weapon("Iron Sword", strength=4, grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[], items=[sword])

        state.apply_key("w")

        assert player.weapon is sword, "Sword should be auto-equipped on pickup"

    def test_t010_stronger_weapon_replaces_weaker(self):
        """T010: a stronger weapon replaces a weaker one."""
        player = _make_player(location=(5, 5), facing="north")
        dagger = _make_weapon("Dagger", strength=2, grid_x=5, grid_y=6)
        # Pre-equip the dagger via pickup on first step
        state = _make_state(player, enemies=[], items=[dagger])
        state.apply_key("w")
        assert player.weapon is dagger

        # Now the player is at (5, 6); move north to (5, 7) where the axe waits
        player.location = (5, 6)
        axe = _make_weapon("Battle Axe", strength=7, grid_x=5, grid_y=7)
        state.floors[0] = (state.grid, player.location, player.facing,
                           state.enemies, [axe], None)

        state.apply_key("w")

        assert player.weapon is axe, "Stronger axe should replace weaker dagger"

    def test_t010_weaker_weapon_does_not_replace_stronger(self):
        """T010: a weaker weapon does NOT replace a better-equipped weapon."""
        player = _make_player(location=(5, 5), facing="north")
        axe = _make_weapon("Battle Axe", strength=7, grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[], items=[axe])
        state.apply_key("w")
        assert player.weapon is axe

        player.location = (5, 6)
        dagger = _make_weapon("Dagger", strength=2, grid_x=5, grid_y=7)
        state.floors[0] = (state.grid, player.location, player.facing,
                           state.enemies, [dagger], None)

        state.apply_key("w")

        assert player.weapon is axe, "Weaker dagger must not replace the equipped axe"

    def test_t010_non_weapon_does_not_replace_equipped_weapon(self):
        """T010: picking up a non-weapon item does not change the equipped weapon."""
        player = _make_player(location=(5, 5), facing="north")
        sword = _make_weapon("Iron Sword", strength=4, grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[], items=[sword])
        state.apply_key("w")
        assert player.weapon is sword

        player.location = (5, 6)
        coin = _make_item("Gold Coin", 5, "Coin", grid_x=5, grid_y=7,
                          category="treasure")
        state.floors[0] = (state.grid, player.location, player.facing,
                           state.enemies, [coin], None)

        state.apply_key("w")

        assert player.weapon is sword, "Non-weapon pickup must not change equipped weapon"

    def test_t011_weapon_bonus_applied_in_combat(self, always_hit):
        """T011: after equipping a weapon via pickup, strike() includes the weapon bonus."""
        player = _make_player(location=(5, 5), facing="north")
        base_strength = player.strength  # e.g. 1

        sword = _make_weapon("Iron Sword", strength=4, grid_x=5, grid_y=6)
        state = _make_state(player, enemies=[], items=[sword])
        state.apply_key("w")  # collect sword at (5,6)

        # Confirm weapon is equipped
        assert player.weapon is sword, "Sword should be equipped"

        # Create an enemy with high HP at a position we can strike
        goblin = Enemy("Goblin", hp=100, attack=1, speed=1, grid_x=5, grid_y=7)
        state.enemies = [goblin]
        state.floors[0] = (state.grid, player.location, player.facing,
                           state.enemies, [], None)

        player.strike(goblin)

        expected_damage = base_strength + sword.strength
        assert goblin.hp == 100 - expected_damage, \
            f"Expected damage {expected_damage} (base {base_strength} + weapon {sword.strength})"


# ─────────────────────────────────────────────────────────────────────────────
# User Story 3 — Persist inventory across save/load
# ─────────────────────────────────────────────────────────────────────────────

class TestPersistence:
    """T014–T018: schema version, round-trip, no-respawn, legacy compat, future-version guard."""

    def test_t014_schema_version_is_2(self, state_file):
        """T014: SCHEMA_VERSION constant equals 2 and save() writes schema_version 2."""
        assert gs.SCHEMA_VERSION == 2, \
            f"Expected SCHEMA_VERSION == 2, got {gs.SCHEMA_VERSION}"

        player = _make_player()
        state = _make_state(player, enemies=[], items=[])
        state.dungeon_path = "DebugMapLoader.dngn"
        state.save()

        with open(state_file) as f:
            data = json.load(f)
        assert data["schema_version"] == 2, \
            f"save() wrote schema_version={data['schema_version']}, expected 2"

    def test_t015_inventory_and_weapon_roundtrip(self, state_file):
        """T015: inventory + equipped weapon survive save() → from_save()."""
        # Build a real dungeon state so from_save() can re-parse it
        _, _, floors = _load_debug_dungeon()

        player = Player("Hero")
        player.location = (2, 1)
        player.facing = "north"

        sword = _make_weapon("Iron Sword", strength=4, grid_x=0, grid_y=0)
        coin = _make_item("Gold Coin", 5, "Coin", grid_x=0, grid_y=1)

        # Simulate having picked up both items
        if not hasattr(player, "inventory"):
            # Feature not yet implemented — fail here with a clear message
            pytest.fail(
                "Player has no 'inventory' attribute — feature not implemented yet"
            )
        player.inventory = [sword, coin]
        player.weapon = sword

        state = GameState("DebugMapLoader.dngn", floors, 0, player, [])
        state.save()

        restored = GameState.from_save()

        assert hasattr(restored.player, "inventory"), "Restored player must have inventory"
        assert len(restored.player.inventory) == 2, \
            f"Expected 2 inventory items, got {len(restored.player.inventory)}"
        restored_names = {i.name for i in restored.player.inventory}
        assert restored_names == {"Iron Sword", "Gold Coin"}, \
            f"Restored inventory names mismatch: {restored_names}"
        assert restored.player.weapon is not None, "Equipped weapon must be restored"
        assert restored.player.weapon.name == "Iron Sword", \
            f"Restored weapon name mismatch: {restored.player.weapon.name}"
        # Equipped weapon must be the same object as the inventory entry (not a duplicate)
        assert restored.player.weapon in restored.player.inventory, \
            "Restored weapon must be an item in the restored inventory"

    def test_t016_collected_item_does_not_respawn(self, state_file):
        """T016: after collect → save → reload, the item is absent from its origin floor."""
        _, _, floors = _load_debug_dungeon()

        player = Player("Hero")
        player.location = (2, 1)
        player.facing = "north"

        # Place a sword on floor 0 at a known position
        sword = _make_weapon("Iron Sword", strength=4, grid_x=1, grid_y=2)
        grid, start_pos, start_facing, enemies, items, stairs = floors[0]
        items_with_sword = list(items) + [sword]
        floors = list(floors)
        floors[0] = (grid, start_pos, start_facing, enemies, items_with_sword, stairs)

        state = GameState("DebugMapLoader.dngn", floors, 0, player, [])

        # Simulate pickup: add to inventory and remove from floor
        if not hasattr(player, "inventory"):
            pytest.fail(
                "Player has no 'inventory' attribute — feature not implemented yet"
            )
        player.inventory = [sword]
        sword.origin_floor = 0  # the feature stamps this on pickup
        state.items.remove(sword)
        state.save()

        restored = GameState.from_save()

        floor0_items = restored.floors[0][4]
        floor0_item_names = [i.name for i in floor0_items]
        assert "Iron Sword" not in floor0_item_names, \
            f"Collected Iron Sword should not reappear on floor 0; found: {floor0_item_names}"

    def test_t017_legacy_v1_save_loads_with_empty_inventory(self, monkeypatch):
        """T017: loading legacy_save_v1.json yields empty inventory and weapon=None."""
        monkeypatch.setattr(gs, "STATE_FILE", str(FIXTURES / "legacy_save_v1.json"))

        state = GameState.from_save()
        p = state.player

        # All state that was in the v1 save must still restore correctly
        assert p.location == (1, 1), f"location mismatch: {p.location}"
        assert p.facing == "north", f"facing mismatch: {p.facing}"
        assert p.hp == 10, f"hp mismatch: {p.hp}"
        assert p.mp == 1, f"mp mismatch: {p.mp}"

        # New fields must default gracefully
        assert hasattr(p, "inventory"), "Restored player must have inventory attribute"
        assert p.inventory == [], f"Expected empty inventory from v1 save, got: {p.inventory}"
        assert p.weapon is None, f"Expected weapon=None from v1 save, got: {p.weapon}"

    def test_t018_future_schema_version_raises_value_error(self, tmp_path, monkeypatch):
        """T018: a save with schema_version 3 raises ValueError on load."""
        path = str(tmp_path / "future_save.json")
        monkeypatch.setattr(gs, "STATE_FILE", path)
        payload = {
            "schema_version": 3,
            "dungeon": "DebugMapLoader.dngn",
            "floor": 0,
            "x": 1,
            "y": 1,
            "facing": "north",
            "hp": 10,
            "mp": 1,
            "xp": 0,
            "level": 1,
            "enemies": [],
        }
        with open(path, "w") as f:
            json.dump(payload, f)

        with pytest.raises(ValueError, match="3") as exc_info:
            GameState.from_save()
        # The error message should also mention the supported version
        assert "2" in str(exc_info.value), \
            f"ValueError should mention supported version 2: {exc_info.value}"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helper for round-trip tests (loads the real DebugMapLoader.dngn)
# ─────────────────────────────────────────────────────────────────────────────

def _load_debug_dungeon():
    """Load DebugMapLoader.dngn via map_loader (same approach as test_schema_version.py)."""
    import map_loader
    map_loader.debug = False
    return map_loader.load_map_file("DebugMapLoader.dngn")
