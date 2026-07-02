from wiz_drive.item import get_item_stats, ITEM_TYPES


DEFAULT_STATS = {"value": 1, "category": "misc", "description": ""}


def test_known_item_returns_library_entry():
    assert get_item_stats("Iron Sword") is ITEM_TYPES["Iron Sword"]


def test_weapon_has_strength_effect():
    stats = get_item_stats("Iron Sword")
    assert stats["category"] == "weapon"
    assert stats["strength"] == 4


def test_consumable_has_heal_effect():
    stats = get_item_stats("Health Potion")
    assert stats["category"] == "consumable"
    assert stats["heal"] == 15


def test_treasure_has_no_effect_keys():
    stats = get_item_stats("Gold Coin")
    assert set(stats.keys()) == {"value", "category", "description"}
    assert stats["category"] == "treasure"


def test_unknown_name_returns_default():
    assert get_item_stats("DefinitelyNotAnItem") == DEFAULT_STATS


def test_empty_string_returns_default():
    assert get_item_stats("") == DEFAULT_STATS


def test_lowercase_name_is_unknown():
    assert get_item_stats("iron sword") == DEFAULT_STATS


def test_every_entry_has_required_keys():
    for name, stats in ITEM_TYPES.items():
        assert {"value", "category", "description"} <= set(stats.keys()), name


def test_every_entry_value_is_positive():
    for name, stats in ITEM_TYPES.items():
        assert stats["value"] > 0, name
