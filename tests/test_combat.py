import pytest
from gameState import GameState, PLAYER_ATTACK
from player import Player
from enemy import Enemy


def _make_player(hp=20):
    return Player("Hero", hp=hp, mp=10)


def _make_enemy(name="Goblin", hp=10, attack=3, grid_x=1, grid_y=1):
    return Enemy(name, hp=hp, attack=attack, speed=1, grid_x=grid_x, grid_y=grid_y)


def _make_state(player, enemies, grid=None):
    if grid is None:
        grid = [[0] * 10 for _ in range(10)]
    floor_data = (grid, player.location, player.facing, list(enemies), [], None)
    return GameState("dummy.dngn", [floor_data], 0, player, list(enemies))


class TestDoCombat:
    def test_player_deals_PLAYER_ATTACK_damage(self):
        p = _make_player()
        e = _make_enemy(hp=50)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert e.hp == 50 - PLAYER_ATTACK

    def test_enemy_at_exact_threshold_is_defeated(self):
        p = _make_player()
        e = _make_enemy(hp=PLAYER_ATTACK)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert state.enemies == []

    def test_enemy_below_threshold_is_defeated(self):
        p = _make_player()
        e = _make_enemy(hp=PLAYER_ATTACK - 1)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert state.enemies == []

    def test_defeated_enemy_does_not_counter_attack(self):
        p = _make_player(hp=20)
        e = _make_enemy(hp=PLAYER_ATTACK, attack=99)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert p.hp == 20

    def test_surviving_enemy_counter_attacks(self):
        p = _make_player(hp=20)
        e = _make_enemy(hp=50, attack=7)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert p.hp == 20 - 7

    def test_surviving_enemy_stays_in_list(self):
        p = _make_player()
        e = _make_enemy(hp=50)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert e in state.enemies

    def test_player_defeated_hp_at_or_below_zero(self):
        p = _make_player(hp=3)
        e = _make_enemy(hp=50, attack=10)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert p.hp <= 0

    def test_player_defeated_enemy_still_in_list(self):
        p = _make_player(hp=1)
        e = _make_enemy(hp=50, attack=10)
        state = _make_state(p, [e])
        state._do_combat(e)
        assert len(state.enemies) == 1

    def test_only_target_removed_not_bystander(self):
        p = _make_player()
        target = _make_enemy(name="Rat", hp=1, attack=1, grid_x=1, grid_y=1)
        bystander = _make_enemy(name="Dragon", hp=50, attack=15, grid_x=3, grid_y=3)
        state = _make_state(p, [target, bystander])
        state._do_combat(target)
        assert target not in state.enemies
        assert bystander in state.enemies

    def test_PLAYER_ATTACK_constant_is_5(self):
        assert PLAYER_ATTACK == 5


class TestIsWall:
    GRID = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ]

    def _make_wall_state(self):
        p = Player("Hero", hp=20, mp=10)
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
    state = _make_state(p, [])
    assert state._next_pos() == expected_next
    assert state._behind_pos() == expected_behind
