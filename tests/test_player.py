import pytest
from wiz_drive.player import Player


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


class TestPlayerAttributes:
    def test_default_attributes(self):
        p = Player("Hero")
        assert p.attack == 0.5
        assert p.strength == 1
        assert p.defense == 1
        assert p.max_hp == 10
        assert p.intelligence == 1
        assert p.mana == 1

    def test_no_weapon_by_default(self):
        assert Player("Hero").weapon is None

    def test_hp_defaults_to_max_hp(self):
        assert Player("Hero").hp == 10

    def test_mp_defaults_to_mana(self):
        assert Player("Hero").mp == 1

    def test_explicit_hp_overrides_default(self):
        assert Player("Hero", hp=25).hp == 25

    def test_explicit_mp_overrides_default(self):
        assert Player("Hero", mp=8).mp == 8

    def test_attributes_are_overridable(self):
        p = Player("Hero", attack=0.75, strength=4, defense=2, max_hp=30,
                   intelligence=6, mana=12)
        assert (p.attack, p.strength, p.defense, p.max_hp, p.intelligence, p.mana) == \
            (0.75, 4, 2, 30, 6, 12)


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
