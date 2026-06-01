import json
import pytest
import ClaudeCodeVisualizer as ccv
from player import Player
from enemy import Enemy


@pytest.fixture
def state_file(tmp_path, monkeypatch):
    path = str(tmp_path / "game_state.json")
    monkeypatch.setattr(ccv, "STATE_FILE", path)
    return path


def _make_player(hp=15, mp=8, location=(2, 3), facing="east"):
    p = Player("Hero", hp=hp, mp=mp)
    p.location = location
    p.facing = facing
    return p


def _make_enemy(**kwargs):
    defaults = dict(name="Goblin", hp=7, attack=3, speed=1, grid_x=2, grid_y=2)
    defaults.update(kwargs)
    return Enemy(**defaults)


class TestSaveLoadRoundTrip:
    def test_dungeon_path_persists(self, state_file):
        ccv.save_state("path/to/dungeon.dngn", 0, _make_player(), [])
        assert ccv.load_state()["dungeon"] == "path/to/dungeon.dngn"

    def test_floor_index_persists(self, state_file):
        ccv.save_state("dungeon.dngn", 2, _make_player(), [])
        assert ccv.load_state()["floor"] == 2

    def test_player_x_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(location=(4, 7)), [])
        assert ccv.load_state()["x"] == 4

    def test_player_y_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(location=(4, 7)), [])
        assert ccv.load_state()["y"] == 7

    def test_player_facing_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(facing="south"), [])
        assert ccv.load_state()["facing"] == "south"

    def test_player_hp_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(hp=13), [])
        assert ccv.load_state()["hp"] == 13

    def test_player_mp_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(mp=5), [])
        assert ccv.load_state()["mp"] == 5

    def test_empty_enemies_list_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [])
        assert ccv.load_state()["enemies"] == []

    def test_enemy_name_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(name="Troll")])
        assert ccv.load_state()["enemies"][0]["name"] == "Troll"

    def test_enemy_hp_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(hp=3)])
        assert ccv.load_state()["enemies"][0]["hp"] == 3

    def test_enemy_attack_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(attack=9)])
        assert ccv.load_state()["enemies"][0]["attack"] == 9

    def test_enemy_speed_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(speed=2)])
        assert ccv.load_state()["enemies"][0]["speed"] == 2

    def test_enemy_grid_x_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(grid_x=4)])
        assert ccv.load_state()["enemies"][0]["grid_x"] == 4

    def test_enemy_grid_y_persists(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [_make_enemy(grid_y=6)])
        assert ccv.load_state()["enemies"][0]["grid_y"] == 6

    def test_multiple_enemies_all_persist(self, state_file):
        enemies = [_make_enemy(name="Rat", grid_x=1), _make_enemy(name="Spider", grid_x=3)]
        ccv.save_state("d.dngn", 0, _make_player(), enemies)
        saved = ccv.load_state()["enemies"]
        assert len(saved) == 2
        assert {e["name"] for e in saved} == {"Rat", "Spider"}

    def test_output_is_valid_json(self, state_file):
        ccv.save_state("d.dngn", 0, _make_player(), [])
        with open(state_file) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_overwrite_updates_floor(self, state_file):
        p = _make_player()
        ccv.save_state("d.dngn", 0, p, [])
        ccv.save_state("d.dngn", 1, p, [])
        assert ccv.load_state()["floor"] == 1
