import pytest
from player import Player


class TestPlayerInit:
    def test_initial_location_is_origin(self):
        p = Player("Hero", hp=20, mp=10)
        assert p.location == (0, 0)

    def test_initial_facing_is_north(self):
        p = Player("Hero", hp=20, mp=10)
        assert p.facing == "north"

    def test_name_stored(self):
        p = Player("Merlin", hp=15, mp=30)
        assert p.name == "Merlin"

    def test_hp_and_mp_stored(self):
        p = Player("Hero", hp=15, mp=7)
        assert p.hp == 15
        assert p.mp == 7


@pytest.mark.parametrize("facing,direction,expected", [
    ("north", "forward",  (0,  1)),
    ("north", "backward", (0, -1)),
    ("south", "forward",  (0, -1)),
    ("south", "backward", (0,  1)),
    ("east",  "forward",  (1,  0)),
    ("east",  "backward", (-1, 0)),
    ("west",  "forward",  (-1, 0)),
    ("west",  "backward", (1,  0)),
])
def test_move_from_origin(facing, direction, expected):
    p = Player("Hero", hp=20, mp=10)
    p.facing = facing
    p.move(direction)
    assert p.location == expected


def test_move_accumulates():
    p = Player("Hero", hp=20, mp=10)
    p.facing = "east"
    p.move("forward")
    p.move("forward")
    assert p.location == (2, 0)


def test_move_invalid_direction_raises():
    p = Player("Hero", hp=20, mp=10)
    with pytest.raises(ValueError):
        p.move("strafe")


def test_move_does_not_change_facing():
    p = Player("Hero", hp=20, mp=10)
    p.facing = "north"
    p.move("forward")
    assert p.facing == "north"


def test_turn_right_full_cycle():
    p = Player("Hero", hp=20, mp=10)
    sequence = []
    for _ in range(5):
        sequence.append(p.facing)
        p.turn("right")
    assert sequence == ["north", "east", "south", "west", "north"]


def test_turn_left_full_cycle():
    p = Player("Hero", hp=20, mp=10)
    sequence = []
    for _ in range(5):
        sequence.append(p.facing)
        p.turn("left")
    assert sequence == ["north", "west", "south", "east", "north"]


def test_turn_right_then_left_returns_to_start():
    p = Player("Hero", hp=20, mp=10)
    p.turn("right")
    p.turn("left")
    assert p.facing == "north"


def test_turn_invalid_direction_raises():
    p = Player("Hero", hp=20, mp=10)
    with pytest.raises(ValueError):
        p.turn("forward")


def test_turn_does_not_change_location():
    p = Player("Hero", hp=20, mp=10)
    p.turn("right")
    assert p.location == (0, 0)
