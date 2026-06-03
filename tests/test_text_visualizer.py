import pytest
from text_visualizer import render_floor
from enemy import Enemy
from item import Item


def _grid():
    """5×5 open-interior grid: perimeter walls, 3×3 open interior."""
    return [
        [1, 1, 1, 1, 1],  # y=0 (bottom)
        [1, 0, 0, 0, 1],  # y=1
        [1, 0, 0, 0, 1],  # y=2 (middle)
        [1, 0, 0, 0, 1],  # y=3
        [1, 1, 1, 1, 1],  # y=4 (top)
    ]


def _render(player_pos, facing="north", enemies=None, items=None, stairs=None, floor_num=1):
    render_floor((_grid(), player_pos, facing, enemies or [], items or [], stairs), floor_num)


class TestHeader:
    def test_floor_header_present(self, capsys):
        _render((1, 1))
        out = capsys.readouterr().out
        assert "--- Floor 1 ---" in out

    def test_floor_header_uses_floor_num_arg(self, capsys):
        render_floor((_grid(), (1, 1), "north", [], [], None), 3)
        out = capsys.readouterr().out
        assert "--- Floor 3 ---" in out


class TestGridSymbols:
    def test_top_row_is_all_walls(self, capsys):
        # Grid row y=4 (all walls) is printed first after the header.
        _render((1, 1))
        lines = capsys.readouterr().out.splitlines()
        assert lines[1] == "#####"

    def test_bottom_row_is_all_walls(self, capsys):
        _render((1, 1))
        lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
        facing_idx = next(i for i, l in enumerate(lines) if "Player facing:" in l)
        assert lines[facing_idx - 1] == "#####"

    def test_open_tile_renders_as_dot(self, capsys):
        _render((2, 2))
        out = capsys.readouterr().out
        assert "." in out

    def test_player_renders_as_at(self, capsys):
        _render((2, 2))
        out = capsys.readouterr().out
        assert "@" in out

    def test_enemy_renders_as_E(self, capsys):
        e = Enemy("Goblin", hp=10, attack=3, speed=1, grid_x=3, grid_y=1)
        _render((1, 3), enemies=[e])
        out = capsys.readouterr().out
        assert "E" in out

    def test_item_renders_as_I(self, capsys):
        it = Item("Gold", 5, "shiny", 3, 1)
        _render((1, 3), items=[it])
        out = capsys.readouterr().out
        assert "I" in out

    def test_stairs_renders_as_gt(self, capsys):
        _render((1, 3), stairs=(3, 1))
        out = capsys.readouterr().out
        assert ">" in out


class TestRenderPriority:
    # Grid is printed top-to-bottom: lines[1]=y=4, lines[2]=y=3, lines[3]=y=2,
    # lines[4]=y=1, lines[5]=y=0. So tile (2, 2) is at lines[3].

    def test_player_beats_enemy_on_same_tile(self, capsys):
        e = Enemy("Goblin", hp=10, attack=3, speed=1, grid_x=2, grid_y=2)
        _render((2, 2), enemies=[e])
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "@" in row
        assert "E" not in row

    def test_player_beats_item_on_same_tile(self, capsys):
        it = Item("Gold", 5, "shiny", 2, 2)
        _render((2, 2), items=[it])
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "@" in row
        assert "I" not in row

    def test_player_beats_stairs_on_same_tile(self, capsys):
        _render((2, 2), stairs=(2, 2))
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "@" in row
        assert ">" not in row

    def test_enemy_beats_item_on_same_tile(self, capsys):
        e = Enemy("Goblin", hp=10, attack=3, speed=1, grid_x=2, grid_y=2)
        it = Item("Gold", 5, "shiny", 2, 2)
        _render((1, 1), enemies=[e], items=[it])
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "E" in row
        assert "I" not in row

    def test_enemy_beats_stairs_on_same_tile(self, capsys):
        e = Enemy("Goblin", hp=10, attack=3, speed=1, grid_x=2, grid_y=2)
        _render((1, 1), enemies=[e], stairs=(2, 2))
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "E" in row
        assert ">" not in row

    def test_item_beats_stairs_on_same_tile(self, capsys):
        it = Item("Gold", 5, "shiny", 2, 2)
        _render((1, 1), items=[it], stairs=(2, 2))
        lines = capsys.readouterr().out.splitlines()
        row = lines[3]
        assert "I" in row
        assert ">" not in row


class TestFacingLine:
    @pytest.mark.parametrize("facing,expected", [
        ("north", "^ (North)"),
        ("south", "v (South)"),
        ("east",  "> (East)"),
        ("west",  "< (West)"),
    ])
    def test_facing_arrow_all_directions(self, facing, expected, capsys):
        _render((1, 1), facing=facing)
        out = capsys.readouterr().out
        assert expected in out

    def test_facing_line_present(self, capsys):
        _render((1, 1))
        out = capsys.readouterr().out
        assert "Player facing:" in out
