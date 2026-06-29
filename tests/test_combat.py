import types

import pytest
import wiz_drive.player as player_module
from wiz_drive.game_state import GameState
from wiz_drive.player import Player
from wiz_drive.enemy import Enemy
from wiz_drive.item import Item


@pytest.fixture
def always_hit(monkeypatch):
    # Forces every strike's hit roll to succeed (random.random() < self.attack).
    monkeypatch.setattr(player_module.random, "random", lambda: 0.0)


@pytest.fixture
def always_miss(monkeypatch):
    # Forces every strike's hit roll to fail.
    monkeypatch.setattr(player_module.random, "random", lambda: 0.99)


def _make_player(hp=20):
    return Player("Hero", hp=hp)


def _make_enemy(name="Goblin", hp=10, attack=3, grid_x=1, grid_y=1):
    return Enemy(name, hp=hp, attack=attack, speed=1, grid_x=grid_x, grid_y=grid_y)


def _make_state(player, enemies, grid=None):
    if grid is None:
        grid = [[0] * 10 for _ in range(10)]
    floor_data = (grid, player.location, player.facing, list(enemies), [], None)
    return GameState("dummy.dngn", [floor_data], 0, player, list(enemies))


class TestPlayerStrike:
    def test_hit_deals_strength_damage(self, always_hit):
        p = _make_player()
        e = _make_enemy(hp=50)
        p.strike(e)
        assert e.hp == 50 - p.strength

    def test_hit_adds_weapon_strength(self, always_hit):
        p = _make_player()
        p.weapon = types.SimpleNamespace(strength=4)
        e = _make_enemy(hp=50)
        p.strike(e)
        assert e.hp == 50 - (p.strength + 4)

    def test_miss_deals_no_enemy_damage(self, always_miss):
        p = _make_player()
        e = _make_enemy(hp=50)
        p.strike(e)
        assert e.hp == 50

    def test_enemy_at_exact_threshold_is_defeated(self, always_hit):
        p = _make_player()
        e = _make_enemy(hp=p.strength)
        assert p.strike(e) is True

    def test_enemy_below_threshold_is_defeated(self, always_hit):
        p = _make_player()
        e = _make_enemy(hp=p.strength - 1)
        assert p.strike(e) is True

    def test_defeated_enemy_does_not_counter_attack(self, always_hit):
        p = _make_player(hp=20)
        e = _make_enemy(hp=p.strength, attack=99)
        p.strike(e)
        assert p.hp == 20

    def test_surviving_enemy_counter_attacks(self, always_hit):
        p = _make_player(hp=20)
        e = _make_enemy(hp=50, attack=7)
        p.strike(e)
        assert p.hp == 20 - max(1, 7 - p.defense)

    def test_miss_still_lets_enemy_counter_attack(self, always_miss):
        p = _make_player(hp=20)
        e = _make_enemy(hp=50, attack=7)
        p.strike(e)
        assert p.hp == 20 - max(1, 7 - p.defense)

    def test_counter_damage_floored_at_one(self, always_hit):
        p = _make_player(hp=20)
        e = _make_enemy(hp=50, attack=1)
        p.strike(e)
        assert p.hp == 20 - 1

    def test_surviving_enemy_returns_false(self, always_hit):
        p = _make_player()
        e = _make_enemy(hp=50)
        assert p.strike(e) is False

    def test_player_defeated_hp_at_or_below_zero(self, always_hit):
        p = _make_player(hp=3)
        e = _make_enemy(hp=50, attack=10)
        p.strike(e)
        assert p.hp <= 0

    def test_only_target_removed_not_bystander(self, always_hit):
        p = _make_player()
        target = _make_enemy(name="Rat", hp=1, attack=1, grid_x=1, grid_y=1)
        bystander = _make_enemy(name="Dragon", hp=50, attack=15, grid_x=3, grid_y=3)
        state = _make_state(p, [target, bystander])
        if state.player.strike(target):
            state.enemies.remove(target)
        assert target not in state.enemies
        assert bystander in state.enemies


class TestIsWall:
    GRID = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]

    def _make_wall_state(self):
        p = Player("Hero", hp=20)
        floor_data = (self.GRID, (0, 0), "north", [], [], None)
        return GameState("dummy.dngn", [floor_data], 0, p, [])

    def test_wall_tile_returns_true(self):
        assert self._make_wall_state()._is_wall(0, 0) is True

    def test_open_tile_returns_false(self):
        assert self._make_wall_state()._is_wall(1, 1) is False

    def test_negative_x_returns_true(self):
        assert self._make_wall_state()._is_wall(-1, 1) is True

    def test_negative_y_returns_true(self):
        assert self._make_wall_state()._is_wall(1, -1) is True

    def test_x_equal_to_size_returns_true(self):
        assert self._make_wall_state()._is_wall(3, 1) is True

    def test_y_equal_to_size_returns_true(self):
        assert self._make_wall_state()._is_wall(1, 3) is True

    def test_far_out_of_bounds_returns_true(self):
        assert self._make_wall_state()._is_wall(100, 100) is True


class TestItemPickup:
    # Player starts at (1, 1) facing north; north delta is (0, +1), so a forward
    # step ("w") lands on (1, 2).
    def _make_item_state(self, items, grid=None):
        if grid is None:
            grid = [[0] * 10 for _ in range(10)]
        p = Player("Hero", hp=20)
        p.location = (1, 1)
        p.facing = "north"
        floor_data = (grid, p.location, p.facing, [], list(items), None)
        return GameState("dummy.dngn", [floor_data], 0, p, [])

    def test_walking_onto_item_adds_it_to_inventory(self):
        item = Item("Gold Coin", 5, "shiny", grid_x=1, grid_y=2)
        state = self._make_item_state([item])
        state.apply_key("w")
        assert item in state.player.inventory

    def test_walking_onto_item_removes_it_from_the_floor(self):
        item = Item("Gold Coin", 5, "shiny", grid_x=1, grid_y=2)
        state = self._make_item_state([item])
        state.apply_key("w")
        assert item not in state.items

    def test_collected_item_is_not_picked_up_again_on_return(self):
        item = Item("Gold Coin", 5, "shiny", grid_x=1, grid_y=2)
        state = self._make_item_state([item])
        state.apply_key("w")          # step onto (1, 2), pick it up
        state.apply_key("s")          # step back to (1, 1)
        state.apply_key("w")          # step onto (1, 2) again — nothing left
        assert state.player.inventory == [item]

    def test_only_the_item_on_the_tile_is_collected(self):
        here = Item("Gold Coin", 5, "shiny", grid_x=1, grid_y=2)
        elsewhere = Item("Iron Sword", 30, "blade", grid_x=5, grid_y=5)
        state = self._make_item_state([here, elsewhere])
        state.apply_key("w")
        assert state.player.inventory == [here]
        assert elsewhere in state.items

    def test_walking_onto_empty_tile_does_not_pick_up_or_crash(self):
        # Regression: the move-onto-open-tile branch calls _item_at, which must
        # exist (an earlier version crashed with AttributeError here).
        state = self._make_item_state([])
        state.apply_key("w")
        assert state.player.location == (1, 2)
        assert state.player.inventory == []


@pytest.mark.parametrize("facing,expected_next,expected_prev", [
    ("north", (3, 4), (3, 2)),
    ("south", (3, 2), (3, 4)),
    ("east",  (4, 3), (2, 3)),
    ("west",  (2, 3), (4, 3)),
])
def test_next_and_prev_pos(facing, expected_next, expected_prev):
    p = Player("Hero", hp=20)
    p.location = (3, 3)
    p.facing = facing
    assert p.next_pos() == expected_next
    assert p.prev_pos() == expected_prev
