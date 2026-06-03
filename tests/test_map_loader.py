import textwrap
import pytest
from map_loader import load_map_text, load_map_file


MINIMAL_3x3 = textwrap.dedent("""\
    Tiny Dungeon
    1

    3
    1 1 1
    1 0 1
    1 1 1
    1 1
    N
""")

OPEN_5x5 = textwrap.dedent("""\
    Open Dungeon
    1

    5
    1 1 1 1 1
    1 0 0 0 1
    1 0 0 0 1
    1 0 0 0 1
    1 1 1 1 1
    1 1
    N
""")


class TestLoadMapTextBasic:
    def test_returns_correct_name(self):
        name, _, _ = load_map_text(MINIMAL_3x3)
        assert name == "Tiny Dungeon"

    def test_returns_declared_floor_count(self):
        _, num, _ = load_map_text(MINIMAL_3x3)
        assert num == 1

    def test_returns_one_floor(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        assert len(floors) == 1

    def test_floor_is_six_tuple(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        assert len(floors[0]) == 6

    def test_player_pos_correct(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        _, pos, _, _, _, _ = floors[0]
        assert pos == (1, 1)

    def test_facing_north(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        _, _, facing, _, _, _ = floors[0]
        assert facing == "north"

    def test_facing_accepts_lowercase_n(self):
        text = OPEN_5x5.replace("\nN\n", "\nn\n")
        _, _, floors = load_map_text(text)
        _, _, facing, _, _, _ = floors[0]
        assert facing == "north"

    def test_facing_accepts_full_word_east(self):
        text = OPEN_5x5.replace("\nN\n", "\neast\n")
        _, _, floors = load_map_text(text)
        _, _, facing, _, _, _ = floors[0]
        assert facing == "east"

    def test_no_enemies_or_items_initially(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        _, _, _, enemies, items, _ = floors[0]
        assert enemies == []
        assert items == []

    def test_stairs_none_when_absent(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        _, _, _, _, _, stairs = floors[0]
        assert stairs is None


class TestGridReversal:
    def test_file_row_0_becomes_top_y_index(self):
        # File rows 0-1 are all-walls; rows 2-4 have open interiors.
        # After reversal: file row 0 → grid[4], file row 4 → grid[0].
        text = textwrap.dedent("""\
            Reversal Test
            1

            5
            1 1 1 1 1
            1 1 1 1 1
            1 0 0 0 1
            1 0 0 0 1
            1 0 0 0 1
            1 2
            N
        """)
        _, _, floors = load_map_text(text)
        grid, _, _, _, _, _ = floors[0]
        assert grid[4] == [1, 1, 1, 1, 1]
        assert grid[3] == [1, 1, 1, 1, 1]
        assert grid[0] == [1, 0, 0, 0, 1]

    def test_grid_size_matches_declared_size(self):
        _, _, floors = load_map_text(OPEN_5x5)
        grid, _, _, _, _, _ = floors[0]
        assert len(grid) == 5
        assert all(len(row) == 5 for row in grid)

    def test_grid_values_are_integers(self):
        _, _, floors = load_map_text(MINIMAL_3x3)
        grid, _, _, _, _, _ = floors[0]
        for row in grid:
            for cell in row:
                assert isinstance(cell, int)
                assert cell in (0, 1)


class TestEnemyParsing:
    def test_3field_enemy_uses_library_stats(self):
        text = OPEN_5x5 + "ENEMY|Goblin|3 2\n"
        _, _, floors = load_map_text(text)
        _, _, _, enemies, _, _ = floors[0]
        assert len(enemies) == 1
        e = enemies[0]
        assert e.name == "Goblin"
        assert e.hp == 10
        assert e.attack == 3
        assert e.speed == 1
        assert e.grid_x == 3
        assert e.grid_y == 2

    def test_6field_enemy_uses_explicit_stats(self):
        text = OPEN_5x5 + "ENEMY|CustomBeast|99|12|3|2 3\n"
        _, _, floors = load_map_text(text)
        _, _, _, enemies, _, _ = floors[0]
        e = enemies[0]
        assert e.name == "CustomBeast"
        assert e.hp == 99
        assert e.attack == 12
        assert e.speed == 3
        assert e.grid_x == 2
        assert e.grid_y == 3

    def test_3field_unknown_name_uses_default_stats(self):
        text = OPEN_5x5 + "ENEMY|NoSuchCreature|2 2\n"
        _, _, floors = load_map_text(text)
        _, _, _, enemies, _, _ = floors[0]
        e = enemies[0]
        assert e.hp == 10
        assert e.attack == 3
        assert e.speed == 1

    def test_enemy_on_wall_raises(self):
        text = OPEN_5x5 + "ENEMY|Goblin|0 0\n"
        with pytest.raises(ValueError, match="blocked tile"):
            load_map_text(text)

    def test_enemy_out_of_bounds_raises(self):
        text = OPEN_5x5 + "ENEMY|Goblin|9 9\n"
        with pytest.raises(ValueError, match="out of bounds"):
            load_map_text(text)

    def test_multiple_enemies_all_loaded(self):
        text = OPEN_5x5 + "ENEMY|Goblin|1 1\nENEMY|Rat|2 2\n"
        _, _, floors = load_map_text(text)
        _, _, _, enemies, _, _ = floors[0]
        assert len(enemies) == 2
        assert {e.name for e in enemies} == {"Goblin", "Rat"}

    def test_6field_zero_hp_raises(self):
        text = OPEN_5x5 + "ENEMY|Bad|0|3|1|2 2\n"
        with pytest.raises(ValueError, match="positive"):
            load_map_text(text)


class TestItemParsing:
    def test_item_fields_parsed_correctly(self):
        text = OPEN_5x5 + "ITEM|Gold Coin|5|A shiny gold coin|3 2\n"
        _, _, floors = load_map_text(text)
        _, _, _, _, items, _ = floors[0]
        assert len(items) == 1
        it = items[0]
        assert it.name == "Gold Coin"
        assert it.value == 5
        assert it.description == "A shiny gold coin"
        assert it.grid_x == 3
        assert it.grid_y == 2

    def test_item_on_wall_raises(self):
        text = OPEN_5x5 + "ITEM|Gold|5|desc|0 0\n"
        with pytest.raises(ValueError, match="blocked tile"):
            load_map_text(text)

    def test_item_out_of_bounds_raises(self):
        text = OPEN_5x5 + "ITEM|Gold|5|desc|9 9\n"
        with pytest.raises(ValueError, match="out of bounds"):
            load_map_text(text)

    def test_item_non_integer_value_raises(self):
        text = OPEN_5x5 + "ITEM|Gold|abc|desc|1 1\n"
        with pytest.raises(ValueError, match="integer"):
            load_map_text(text)

    def test_item_zero_value_raises(self):
        text = OPEN_5x5 + "ITEM|Gold|0|desc|1 1\n"
        with pytest.raises(ValueError, match="positive"):
            load_map_text(text)


class TestStairsParsing:
    def test_stairs_parsed_correctly(self):
        text = OPEN_5x5 + "STAIRS|3 2\n"
        _, _, floors = load_map_text(text)
        _, _, _, _, _, stairs = floors[0]
        assert stairs == (3, 2)

    def test_stairs_on_wall_raises(self):
        text = OPEN_5x5 + "STAIRS|0 0\n"
        with pytest.raises(ValueError, match="blocked tile"):
            load_map_text(text)

    def test_stairs_out_of_bounds_raises(self):
        text = OPEN_5x5 + "STAIRS|9 9\n"
        with pytest.raises(ValueError, match="out of bounds"):
            load_map_text(text)

    def test_no_stairs_returns_none(self):
        _, _, floors = load_map_text(OPEN_5x5)
        _, _, _, _, _, stairs = floors[0]
        assert stairs is None


class TestPlayerStartValidation:
    def test_player_on_wall_raises(self):
        text = textwrap.dedent("""\
            Test
            1

            3
            1 1 1
            1 0 1
            1 1 1
            0 0
            N
        """)
        with pytest.raises(ValueError, match="blocked tile"):
            load_map_text(text)

    def test_player_out_of_bounds_raises(self):
        text = textwrap.dedent("""\
            Test
            1

            3
            1 1 1
            1 0 1
            1 1 1
            5 5
            N
        """)
        with pytest.raises(ValueError, match="out of bounds"):
            load_map_text(text)


class TestMultiFloor:
    TWO_FLOOR = textwrap.dedent("""\
        Two Floor Test
        2

        3
        1 1 1
        1 0 1
        1 1 1
        1 1
        N

        4
        1 1 1 1
        1 0 0 1
        1 0 0 1
        1 1 1 1
        1 1
        E
    """)

    def test_two_floors_loaded(self):
        _, _, floors = load_map_text(self.TWO_FLOOR)
        assert len(floors) == 2

    def test_floor_count_declared_correctly(self):
        _, num, _ = load_map_text(self.TWO_FLOOR)
        assert num == 2

    def test_floor1_grid_size(self):
        _, _, floors = load_map_text(self.TWO_FLOOR)
        grid, _, _, _, _, _ = floors[0]
        assert len(grid) == 3

    def test_floor2_grid_size(self):
        _, _, floors = load_map_text(self.TWO_FLOOR)
        grid, _, _, _, _, _ = floors[1]
        assert len(grid) == 4

    def test_floor2_facing_east(self):
        _, _, floors = load_map_text(self.TWO_FLOOR)
        _, _, facing, _, _, _ = floors[1]
        assert facing == "east"

    def test_too_many_floor_blocks_raises(self):
        text = textwrap.dedent("""\
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
        with pytest.raises(ValueError, match="floor definitions"):
            load_map_text(text)


class TestLoadMapFile:
    def test_wrong_extension_raises(self, tmp_path):
        f = tmp_path / "map.txt"
        f.write_text(MINIMAL_3x3)
        with pytest.raises(ValueError, match=r"\.dngn"):
            load_map_file(str(f))

    def test_valid_dngn_file_loads(self, tmp_path):
        f = tmp_path / "map.dngn"
        f.write_text(MINIMAL_3x3)
        name, num, floors = load_map_file(str(f))
        assert name == "Tiny Dungeon"
        assert num == 1
        assert len(floors) == 1
