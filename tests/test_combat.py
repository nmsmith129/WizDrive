import pytest
import ClaudeCodeVisualizer as ccv
from player import Player
from enemy import Enemy


def _make_player(hp=20):
    return Player("Hero", hp=hp, mp=10)


def _make_enemy(name="Goblin", hp=10, attack=3, grid_x=1, grid_y=1):
    return Enemy(name, hp=hp, attack=attack, speed=1, grid_x=grid_x, grid_y=grid_y)


class TestDoCombat:
    def test_player_deals_PLAYER_ATTACK_damage(self):
        p = _make_player()
        e = _make_enemy(hp=50)
        ccv._do_combat(p, e, [e])
        assert e.hp == 50 - ccv.PLAYER_ATTACK

    def test_enemy_at_exact_threshold_is_defeated(self):
        p = _make_player()
        e = _make_enemy(hp=ccv.PLAYER_ATTACK)
        enemies = [e]
        ccv._do_combat(p, e, enemies)
        assert enemies == []

    def test_enemy_below_threshold_is_defeated(self):
        p = _make_player()
        e = _make_enemy(hp=ccv.PLAYER_ATTACK - 1)
        enemies = [e]
        ccv._do_combat(p, e, enemies)
        assert enemies == []

    def test_defeated_enemy_does_not_counter_attack(self):
        p = _make_player(hp=20)
        e = _make_enemy(hp=ccv.PLAYER_ATTACK, attack=99)
        ccv._do_combat(p, e, [e])
        assert p.hp == 20

    def test_surviving_enemy_counter_attacks(self):
        p = _make_player(hp=20)
        e = _make_enemy(hp=50, attack=7)
        ccv._do_combat(p, e, [e])
        assert p.hp == 20 - 7

    def test_surviving_enemy_stays_in_list(self):
        p = _make_player()
        e = _make_enemy(hp=50)
        enemies = [e]
        ccv._do_combat(p, e, enemies)
        assert e in enemies

    def test_player_defeated_hp_at_or_below_zero(self):
        p = _make_player(hp=3)
        e = _make_enemy(hp=50, attack=10)
        ccv._do_combat(p, e, [e])
        assert p.hp <= 0

    def test_player_defeated_enemy_still_in_list(self):
        p = _make_player(hp=1)
        e = _make_enemy(hp=50, attack=10)
        enemies = [e]
        ccv._do_combat(p, e, enemies)
        assert len(enemies) == 1

    def test_only_target_removed_not_bystander(self):
        p = _make_player()
        target = _make_enemy(name="Rat", hp=1, attack=1, grid_x=1, grid_y=1)
        bystander = _make_enemy(name="Dragon", hp=50, attack=15, grid_x=3, grid_y=3)
        enemies = [target, bystander]
        ccv._do_combat(p, target, enemies)
        assert target not in enemies
        assert bystander in enemies

    def test_PLAYER_ATTACK_constant_is_5(self):
        assert ccv.PLAYER_ATTACK == 5


class TestIsWall:
    GRID = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]

    def test_wall_tile_returns_true(self):
        assert ccv._is_wall(self.GRID, 0, 0) is True

    def test_open_tile_returns_false(self):
        assert ccv._is_wall(self.GRID, 1, 1) is False

    def test_negative_x_returns_true(self):
        assert ccv._is_wall(self.GRID, -1, 1) is True

    def test_negative_y_returns_true(self):
        assert ccv._is_wall(self.GRID, 1, -1) is True

    def test_x_equal_to_size_returns_true(self):
        assert ccv._is_wall(self.GRID, 3, 1) is True

    def test_y_equal_to_size_returns_true(self):
        assert ccv._is_wall(self.GRID, 1, 3) is True

    def test_far_out_of_bounds_returns_true(self):
        assert ccv._is_wall(self.GRID, 100, 100) is True


@pytest.mark.parametrize("facing,expected_next,expected_behind", [
    ("north", (3, 4), (3, 2)),
    ("south", (3, 2), (3, 4)),
    ("east",  (4, 3), (2, 3)),
    ("west",  (2, 3), (4, 3)),
])
def test_next_and_behind_pos(facing, expected_next, expected_behind):
    p = Player("Hero", hp=20, mp=10)
    p.location = (3, 3)
    p.facing = facing
    assert ccv._next_pos(p) == expected_next
    assert ccv._behind_pos(p) == expected_behind
