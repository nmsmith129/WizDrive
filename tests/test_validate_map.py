import os
import textwrap
import pytest
from map_loader import validate_map_file


VALID_MAP = textwrap.dedent("""\
    Valid Dungeon
    1

    3
    1 1 1
    1 0 1
    1 1 1
    1 1
    N
""")

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestValidateMapFileValid:
    def test_valid_file_returns_true(self, tmp_path):
        f = tmp_path / "map.dngn"
        f.write_text(VALID_MAP)
        valid, errors = validate_map_file(str(f))
        assert valid is True

    def test_valid_file_returns_empty_error_list(self, tmp_path):
        f = tmp_path / "map.dngn"
        f.write_text(VALID_MAP)
        _, errors = validate_map_file(str(f))
        assert errors == []

    def test_item_shorthand_is_valid(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            1

            5
            1 1 1 1 1
            1 0 0 0 1
            1 0 0 0 1
            1 0 0 0 1
            1 1 1 1 1
            1 1
            N
            ITEM|Iron Sword|2 2
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is True, errors


class TestValidateMapFileErrors:
    def test_nonexistent_file_returns_false(self, tmp_path):
        f = tmp_path / "does_not_exist.dngn"
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert len(errors) >= 1
        assert any("not found" in e.lower() or "File not found" in e for e in errors)

    def test_bad_facing_accumulated(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            1

            3
            1 1 1
            1 0 1
            1 1 1
            1 1
            BADDIR
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert any("Facing direction" in e for e in errors)

    def test_player_on_wall_accumulated(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            1

            3
            1 1 1
            1 0 1
            1 1 1
            0 0
            N
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert any("blocked tile" in e for e in errors)

    def test_multiple_errors_accumulated_in_single_floor(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            1

            5
            1 1 1 1 1
            1 0 0 0 1
            1 0 0 0 1
            1 0 0 0 1
            1 1 1 1 1
            0 0
            BADDIR
            ENEMY|Goblin|0 0
            ITEM|Gold|bad|desc|1 1
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert len(errors) >= 3

    def test_errors_span_multiple_floor_blocks(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            2

            5
            1 1 1 1 1
            1 0 0 0 1
            1 0 0 0 1
            1 0 0 0 1
            1 1 1 1 1
            0 0
            BADDIR

            5
            1 1 1 1 1
            1 0 0 0 1
            1 0 0 0 1
            1 0 0 0 1
            1 1 1 1 1
            5 5
            N
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert any(e.startswith("Floor 1") for e in errors)
        assert any(e.startswith("Floor 2") for e in errors)

    def test_too_many_floors_accumulated(self, tmp_path):
        content = textwrap.dedent("""\
            Test
            1

            3
            1 1 1
            1 0 1
            1 1 1
            1 1
            N

            3
            1 1 1
            1 0 1
            1 1 1
            1 1
            N
        """)
        f = tmp_path / "map.dngn"
        f.write_text(content)
        valid, errors = validate_map_file(str(f))
        assert valid is False
        assert any("floor definitions" in e for e in errors)

    def test_live_test_one_is_valid(self):
        path = os.path.join(REPO_ROOT, "liveTestOne.dngn")
        valid, errors = validate_map_file(path)
        assert valid is True, f"liveTestOne.dngn validation failed: {errors}"

    def test_debug_map_loader_is_valid(self):
        path = os.path.join(REPO_ROOT, "DebugMapLoader.dngn")
        valid, errors = validate_map_file(path)
        assert valid is True, f"DebugMapLoader.dngn validation failed: {errors}"
