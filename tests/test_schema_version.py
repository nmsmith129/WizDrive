import json
import pathlib
import pytest
import wiz_drive.game_state as gs
from wiz_drive.game_state import GameState

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


@pytest.fixture
def legacy_fixture(monkeypatch):
    monkeypatch.setattr(gs, "STATE_FILE", str(FIXTURES / "legacy_save_v0.json"))


@pytest.fixture
def save_file(tmp_path, monkeypatch):
    path = str(tmp_path / "game_state.json")
    monkeypatch.setattr(gs, "STATE_FILE", path)
    return path


def _make_state(dungeon="d.dngn", floor=0, player=None, enemies=None):
    from wiz_drive.player import Player
    if player is None:
        player = Player("Hero")
        player.location = (1, 1)
        player.facing = "north"
    if enemies is None:
        enemies = []
    grid = [[0] * 10 for _ in range(10)]
    floor_data = (grid, player.location, player.facing, list(enemies), [], None)
    return GameState(dungeon, [floor_data] * (floor + 1), floor, player, list(enemies))


# ── User Story 1: legacy v0 save loads correctly ────────────────────────────

def test_legacy_v0_save_loads(legacy_fixture):
    state = GameState.from_save()
    p = state.player
    assert p.location == (1, 1)
    assert p.facing == "north"
    assert p.hp == 10
    assert p.mp == 1
    assert p.xp == 0
    assert p.level == 1
    assert p.attack == 0.5
    assert p.strength == 1
    assert p.defense == 1
    assert p.max_hp == 10
    assert p.intelligence == 1
    assert p.mana == 1


# ── User Story 2: save files include schema_version ──────────────────────────

def test_save_includes_schema_version(save_file):
    _make_state().save()
    with open(save_file) as f:
        data = json.load(f)
    assert "schema_version" in data


def test_save_schema_version_is_1(save_file):
    _make_state().save()
    with open(save_file) as f:
        data = json.load(f)
    assert data["schema_version"] == 1


# ── User Story 3: newer-version saves are rejected ──────────────────────────

def test_newer_version_save_raises(tmp_path, monkeypatch):
    path = str(tmp_path / "future_save.json")
    monkeypatch.setattr(gs, "STATE_FILE", path)
    payload = {
        "schema_version": 2,
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
    with pytest.raises(ValueError, match="2") as exc_info:
        GameState.from_save()
    assert "1" in str(exc_info.value)
