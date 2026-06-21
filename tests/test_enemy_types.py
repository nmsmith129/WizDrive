import pytest
from wiz_drive.enemy import get_stats, ENEMY_TYPES


KNOWN_ENEMIES = [
    ("Rat",       {"hp":  4, "attack":  1, "speed": 1, "xp":   5}),
    ("Spider",    {"hp":  6, "attack":  2, "speed": 1, "xp":  10}),
    ("Goblin",    {"hp": 10, "attack":  3, "speed": 1, "xp":  15}),
    ("Skeleton",  {"hp": 15, "attack":  4, "speed": 1, "xp":  20}),
    ("Zombie",    {"hp": 18, "attack":  4, "speed": 1, "xp":  25}),
    ("Troll",     {"hp": 20, "attack":  5, "speed": 1, "xp":  30}),
    ("Dark Mage", {"hp": 12, "attack":  6, "speed": 1, "xp":  35}),
    ("Orc",       {"hp": 25, "attack":  6, "speed": 1, "xp":  40}),
    ("Wraith",    {"hp":  8, "attack":  7, "speed": 1, "xp":  45}),
    ("Vampire",   {"hp": 22, "attack":  8, "speed": 1, "xp":  50}),
    ("Dragon",    {"hp": 50, "attack": 15, "speed": 1, "xp": 100}),
]

DEFAULT_STATS = {"hp": 10, "attack": 3, "speed": 1, "xp": 0}


@pytest.mark.parametrize("name,expected", KNOWN_ENEMIES)
def test_known_enemy_stats(name, expected):
    assert get_stats(name) == expected


def test_unknown_name_returns_default():
    assert get_stats("DefinitelyNotAnEnemy") == DEFAULT_STATS


def test_empty_string_returns_default():
    assert get_stats("") == DEFAULT_STATS


def test_lowercase_goblin_is_unknown():
    assert get_stats("goblin") == DEFAULT_STATS


def test_uppercase_rat_is_unknown():
    assert get_stats("RAT") == DEFAULT_STATS


def test_dark_mage_extra_whitespace_is_unknown():
    assert get_stats("Dark  Mage") == DEFAULT_STATS


def test_all_11_known_types_in_table():
    assert len(ENEMY_TYPES) == 11


def test_return_value_has_required_keys():
    stats = get_stats("Dragon")
    assert set(stats.keys()) == {"hp", "attack", "speed", "xp"}


def test_default_return_value_has_required_keys():
    stats = get_stats("Nobody")
    assert set(stats.keys()) == {"hp", "attack", "speed", "xp"}
