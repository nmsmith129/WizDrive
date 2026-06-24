"""Map loader for WizDrive.

Map file format:
- Line 1: dungeon name
- Line 2: number of floors N (positive integer)
- Then up to N floor blocks, separated by blank lines. Each block contains:
    - One line: grid size S (map is S x S)
    - Next S lines: rows of 0/1 values (first row listed is the top of the map)
    - Next line: player x y starting coordinates
    - Next line: initial facing (N/E/S/W or north/east/south/west)
    - Zero or more object descriptor lines (any order):
        ENEMY|name|hp|attack|speed|x y      # OR ENEMY|name|x y
        ITEM|name|value|description|x y     # OR ITEM|name|x y

Example:
Dungeon of Doom
2
10
1 1 1 1 1 1 1 1 1 1
1 0 0 0 0 0 0 0 0 1
...
1 1 1 1 1 1 1 1 1 1
2 3
E
ENEMY|Goblin|10|3|2|4 3                     # OR ENEMY|Goblin|4 3
ITEM|Gold Coin|5|A shiny gold coin|6 3      # OR ITEM|Gold Coin|6 3

8
1 1 1 1 1 1 1 1
1 0 0 0 0 0 0 1
...
1 1 1 1 1 1 1 1
3 4
N
"""

from __future__ import annotations

from pathlib import Path

from .enemy import Enemy, get_stats
from .item import Item, get_item_stats

debug = False  # set to True to enable diagnostic output

FACING_MAP = {
    "n": "north",
    "north": "north",
    "e": "east",
    "east": "east",
    "s": "south",
    "south": "south",
    "w": "west",
    "west": "west",
}

# (grid[y][x]: 0=open/1=wall, player start (x, y), facing, enemies, items, stairs (x, y) or None)
floor_data = tuple[list[list[int]], tuple[int, int], str, list[Enemy], list[Item], tuple[int, int] | None]


def parse_row(row_text: str, size: int) -> list[int]:
    # Parses one grid row from the "Next S lines" section of a floor block; each token must be 0 or 1.
    if debug:
        print(f"[DEBUG] parse_row: row_text={row_text!r}, size={size}")
    # Split on any whitespace and drop empty strings to handle irregular spacing.
    values = [token for token in row_text.strip().split() if token != ""]
    # Enforce that each row has exactly `size` tiles to match the declared grid width.
    if len(values) != size:
        raise ValueError(f"Expected {size} values in row, got {len(values)}: {row_text!r}")

    row = []
    for token in values:
        # Only 0 (open tile) and 1 (wall) are valid map values.
        if token not in {"0", "1"}:
            raise ValueError(f"Map row values must be 0 or 1: {token!r}")
        row.append(int(token))
    if debug:
        print(f"[DEBUG] parse_row -> {row}")
    return row


def parse_player_line(line: str, map_size: int) -> tuple[int, int]:
    # Parses the "player x y" line that immediately follows the S grid rows in a floor block.
    if debug:
        print(f"[DEBUG] parse_player_line: line={line!r}, map_size={map_size}")
    tokens = [token for token in line.strip().split() if token != ""]
    if len(tokens) != 2:
        raise ValueError(f"Player position line must contain exactly two numbers: {line!r}")

    try:
        x = int(tokens[0])
        y = int(tokens[1])
    except ValueError as exc:
        raise ValueError(f"Player coordinates must be integers: {line!r}") from exc

    if not (0 <= x < map_size and 0 <= y < map_size):
        raise ValueError(f"Player coordinates out of bounds: ({x}, {y}) for map size {map_size}")

    if debug:
        print(f"[DEBUG] parse_player_line -> ({x}, {y})")
    return x, y


def parse_facing_line(line: str) -> str:
    # Parses the facing direction line (N/E/S/W or full word) that follows the player position line.
    if debug:
        print(f"[DEBUG] parse_facing_line: line={line!r}")
    facing_token = line.strip().lower()
    if facing_token not in FACING_MAP:
        raise ValueError(
            f"Facing must be one of N, E, S, W or north/east/south/west: {line!r}"
        )
    result = FACING_MAP[facing_token]
    if debug:
        print(f"[DEBUG] parse_facing_line -> {result!r}")
    return result


def _parse_enemy_line(line: str, map_size: int) -> Enemy:
    # Parses ENEMY|name|x y (stats from library) or ENEMY|name|hp|attack|speed|x y (explicit stats).
    if debug:
        print(f"[DEBUG] _parse_enemy_line: line={line!r}, map_size={map_size}")
    parts = line.split("|")
    if len(parts) == 3:
        _, name, raw_pos = parts
        if not name.strip():
            raise ValueError(f"ENEMY name must not be empty: {line!r}")
        stats = get_stats(name.strip())
        hp, attack, speed, xp = stats["hp"], stats["attack"], stats["speed"], stats["xp"]
    elif len(parts) == 6:
        _, name, raw_hp, raw_attack, raw_speed, raw_pos = parts
        if not name.strip():
            raise ValueError(f"ENEMY name must not be empty: {line!r}")
        try:
            hp     = int(raw_hp)
            attack = int(raw_attack)
            speed  = int(raw_speed)
        except ValueError:
            raise ValueError(f"ENEMY hp/attack/speed must be integers: {line!r}")
        if hp <= 0 or attack <= 0 or speed <= 0:
            raise ValueError(f"ENEMY hp/attack/speed must be positive: {line!r}")
        xp = get_stats(name.strip())["xp"]
    else:
        raise ValueError(f"ENEMY line must have 3 or 6 pipe-separated fields, got {len(parts)}: {line!r}")
    pos_parts = raw_pos.strip().split()
    if len(pos_parts) != 2:
        raise ValueError(f"ENEMY position must be 'x y', got: {raw_pos!r}")
    try:
        x, y = int(pos_parts[0]), int(pos_parts[1])
    except ValueError:
        raise ValueError(f"ENEMY position coordinates must be integers: {raw_pos!r}")
    if not (0 <= x < map_size and 0 <= y < map_size):
        raise ValueError(f"ENEMY position ({x}, {y}) out of bounds for map size {map_size}")
    if debug:
        print(f"[DEBUG] _parse_enemy_line -> parsed fields: name={name!r}, hp={hp}, attack={attack}, speed={speed}, pos=({x},{y})")
    enemy = Enemy(name.strip(), hp, attack, speed, x, y, xp=xp)
    if debug:
        print(f"[DEBUG] _parse_enemy_line -> Enemy object created:")
        print(f"  .name={enemy.name!r}, .hp={enemy.hp}, .attack={enemy.attack}, .speed={enemy.speed}")
        print(f"  .grid_x={enemy.grid_x}, .grid_y={enemy.grid_y}")
        print(f"  .image={enemy.image}, size={enemy.image.get_size()}")
        print(f"[DEBUG] _parse_enemy_line -> data integrity check: {'PASS' if ok else 'FAIL'}")
    return enemy


def _parse_item_line(line: str, map_size: int) -> Item:
    # Parses ITEM|name|x y (stats from library) or ITEM|name|value|description|x y (explicit value/description).
    if debug:
        print(f"[DEBUG] _parse_item_line: line={line!r}, map_size={map_size}")
    parts = line.split("|")
    if len(parts) == 3:
        _, name, raw_pos = parts
        if not name.strip():
            raise ValueError(f"ITEM name must not be empty: {line!r}")
        stats = get_item_stats(name.strip())
        value, description = stats["value"], stats["description"]
    elif len(parts) == 5:
        _, name, raw_value, description, raw_pos = parts
        if not name.strip():
            raise ValueError(f"ITEM name must not be empty: {line!r}")
        try:
            value = int(raw_value)
        except ValueError:
            raise ValueError(f"ITEM value must be an integer: {line!r}")
        if value <= 0:
            raise ValueError(f"ITEM value must be positive: {line!r}")
        stats = get_item_stats(name.strip())
    else:
        raise ValueError(f"ITEM line must have 3 or 5 pipe-separated fields, got {len(parts)}: {line!r}")
    category = stats["category"]
    effect = {k: v for k, v in stats.items() if k not in ("value", "category", "description")}
    pos_parts = raw_pos.strip().split()
    if len(pos_parts) != 2:
        raise ValueError(f"ITEM position must be 'x y', got: {raw_pos!r}")
    try:
        x, y = int(pos_parts[0]), int(pos_parts[1])
    except ValueError:
        raise ValueError(f"ITEM position coordinates must be integers: {raw_pos!r}")
    if not (0 <= x < map_size and 0 <= y < map_size):
        raise ValueError(f"ITEM position ({x}, {y}) out of bounds for map size {map_size}")
    if debug:
        print(f"[DEBUG] _parse_item_line -> parsed fields: name={name!r}, value={value}, description={description!r}, category={category!r}, effect={effect}, pos=({x},{y})")
    item = Item(name.strip(), value, description.strip(), x, y, category=category, effect=effect)
    if debug:
        print(f"[DEBUG] _parse_item_line -> Item object created:")
        print(f"  .name={item.name!r}, .value={item.value}, .description={item.description!r}")
        print(f"  .grid_x={item.grid_x}, .grid_y={item.grid_y}")
        print(f"  .image={item.image}, size={item.image.get_size()}")
        print(f"[DEBUG] _parse_item_line -> data integrity check: {'PASS' if ok else 'FAIL'}")
    return item


def _split_floor_blocks(lines: list[str]) -> list[list[str]]:
    """Split lines into floor blocks using blank lines as separators."""
    # Receives all raw lines after the two-line header (dungeon name + floor count).
    if debug:
        print(f"[DEBUG] _split_floor_blocks: {len(lines)} input lines")
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)
    if debug:
        print(f"[DEBUG] _split_floor_blocks -> {len(blocks)} block(s), sizes={[len(b) for b in blocks]}")
    return blocks


def _parse_floor_block(lines: list[str]) -> floor_data:
    """Parse one floor block (size, rows, player, facing) and return its data."""
    # Covers: size line, S grid rows, player position, facing direction, and ENEMY/ITEM descriptor lines.
    if debug:
        print(f"[DEBUG] _parse_floor_block: {len(lines)} lines, first={repr(lines[0]) if lines else 'N/A'}")
    if not lines:
        raise ValueError("Empty floor block")

    try:
        size = int(lines[0].strip())
    except ValueError:
        raise ValueError(f"Size line must be an integer, got: {lines[0]!r}")

    if size <= 0:
        raise ValueError("Floor size must be a positive integer")

    if debug:
        print(f"[DEBUG] _parse_floor_block: size={size}, expecting {1 + size + 2} lines, got {len(lines)}")

    expected_lines = 1 + size + 2
    if len(lines) < expected_lines:
        raise ValueError(
            f"Expected at least {expected_lines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    raw_rows = [parse_row(lines[i + 1], size) for i in range(size)]
    grid = raw_rows[::-1]
    if debug:
        print(f"[DEBUG] _parse_floor_block: raw_rows (top-to-bottom as in file):")
        for i, row in enumerate(raw_rows):
            print(f"  file row {i}: {row}")
        print(f"[DEBUG] _parse_floor_block: grid after reversal (y=0 at bottom):")
        for y, row in enumerate(grid):
            print(f"  y={y}: {row}")
    player_x, player_y = parse_player_line(lines[1 + size], size)
    facing = parse_facing_line(lines[2 + size])

    if grid[player_y][player_x] != 0:
        raise ValueError(f"Player start ({player_x}, {player_y}) is on a blocked tile")

    enemies: list[Enemy] = []
    items: list[Item] = []
    stairs: tuple[int, int] | None = None
    for j, obj_line in enumerate(lines[3 + size:], start=1):
        if obj_line.startswith("ENEMY|"):
            enemy = _parse_enemy_line(obj_line, size)
            ex, ey = enemy.grid_x, enemy.grid_y
            if grid[ey][ex] != 0:
                raise ValueError(f"Object line {j}: ENEMY {enemy.name!r} position ({ex}, {ey}) is on a blocked tile")
            enemies.append(enemy)
        elif obj_line.startswith("ITEM|"):
            item = _parse_item_line(obj_line, size)
            ix, iy = item.grid_x, item.grid_y
            if grid[iy][ix] != 0:
                raise ValueError(f"Object line {j}: ITEM {item.name!r} position ({ix}, {iy}) is on a blocked tile")
            items.append(item)
        elif obj_line.startswith("STAIRS|"):
            parts = obj_line.split("|")
            if len(parts) != 2:
                raise ValueError(f"STAIRS line must be 'STAIRS|x y', got: {obj_line!r}")
            pos_parts = parts[1].strip().split()
            if len(pos_parts) != 2:
                raise ValueError(f"STAIRS position must be 'x y', got: {parts[1]!r}")
            try:
                sx, sy = int(pos_parts[0]), int(pos_parts[1])
            except ValueError:
                raise ValueError(f"STAIRS position coordinates must be integers: {parts[1]!r}")
            if not (0 <= sx < size and 0 <= sy < size):
                raise ValueError(f"STAIRS position ({sx}, {sy}) out of bounds for map size {size}")
            if grid[sy][sx] != 0:
                raise ValueError(f"STAIRS position ({sx}, {sy}) is on a blocked tile")
            stairs = (sx, sy)
        else:
            raise ValueError(f"Object line {j}: unrecognised descriptor {obj_line!r}")

    if debug:
        print(f"[DEBUG] _parse_floor_block -> {size}x{size} grid, player=({player_x},{player_y}), facing={facing!r}, {len(enemies)} enemy/enemies, {len(items)} item(s)")
        print(f"[DEBUG] _parse_floor_block: grid with player marked (P):")
        for y, row in enumerate(grid):
            displayed = [("P" if (xi == player_x and y == player_y) else str(v)) for xi, v in enumerate(row)]
            print(f"  y={y}: [{', '.join(displayed)}]")
        for e in enemies:
            print(f"  enemy: {e.name} hp={e.hp} attack={e.attack} speed={e.speed} pos=({e.grid_x},{e.grid_y})")
        for it in items:
            print(f"  item:  {it.name} value={it.value} desc={it.description!r}")
    return grid, (player_x, player_y), facing, enemies, items, stairs


def _parse_map_lines(raw_lines: list[str], source: str) -> tuple[str, int, list[floor_data]]:
    # Reads the two-line header (dungeon name + floor count), then parses each floor block in sequence.
    if debug:
        print(f"[DEBUG] _parse_map_lines: source={source!r}, {len(raw_lines)} raw lines")
    non_empty = [l for l in raw_lines if l.strip() != ""]
    if len(non_empty) < 2:
        raise ValueError(f"'{source}' is too short: missing dungeon name or floor count")

    name = non_empty[0].strip()

    try:
        num_floors = int(non_empty[1].strip())
    except ValueError:
        raise ValueError(f"Second line must be the floor count integer, got: {non_empty[1]!r}")

    if num_floors <= 0:
        raise ValueError("Number of floors must be a positive integer")

    if debug:
        print(f"[DEBUG] _parse_map_lines: name={name!r}, num_floors={num_floors}")

    # Find the index in raw_lines immediately after the second non-empty line.
    header_count = 0
    after_header_start = len(raw_lines)
    for i, line in enumerate(raw_lines):
        if line.strip() != "":
            header_count += 1
            if header_count == 2:
                after_header_start = i + 1
                break

    floor_blocks = _split_floor_blocks(raw_lines[after_header_start:])

    if not floor_blocks:
        raise ValueError(f"No floor data found in '{source}'")

    if len(floor_blocks) > num_floors:
        raise ValueError(
            f"'{source}' contains {len(floor_blocks)} floor definitions but header declares {num_floors}"
        )

    floors: list[floor_data] = []
    for i, block in enumerate(floor_blocks):
        if debug:
            print(f"[DEBUG] _parse_map_lines: parsing floor block {i + 1}/{len(floor_blocks)}")
        try:
            floors.append(_parse_floor_block(block))
        except ValueError as exc:
            raise ValueError(f"Floor {i + 1}: {exc}") from exc

    if debug:
        print(f"[DEBUG] _parse_map_lines -> name={name!r}, num_floors={num_floors}, {len(floors)} floor(s) loaded")
    return name, num_floors, floors


def load_map_file(path: str | Path) -> tuple[str, int, list[floor_data]]:
    """Load a dungeon from a file.

    Returns:
        name: dungeon name.
        num_floors: total number of floors declared in the header.
        floors: list of (grid, player_position, facing) for each floor defined.
                grid[y][x] is the tile at (x, y) with y=0 at the bottom.
    """
    # Entry point for dungeon files on disk; enforces .dngn extension before delegating to _parse_map_lines.
    if debug:
        print(f"[DEBUG] load_map_file: path={str(path)!r}")
    path_obj = Path(path)
    if path_obj.suffix != ".dngn":
        raise ValueError(f"Map file must have a .dngn extension, got: {path_obj.name!r}")
    raw_lines = [line.rstrip() for line in path_obj.read_text(encoding="utf-8").splitlines()]
    if debug:
        print(f"[DEBUG] load_map_file: read {len(raw_lines)} lines from {str(path_obj)!r}")
    result = _parse_map_lines(raw_lines, source=str(path_obj))
    if debug:
        print(f"[DEBUG] load_map_file -> dungeon={result[0]!r}, {result[1]} floor(s) declared, {len(result[2])} loaded")
    return result


def load_map_text(text: str) -> tuple[str, int, list[floor_data]]:
    """Load dungeon data from a string using the same format as load_map_file."""
    # Entry point for in-memory map text; skips the file-read step and delegates directly to _parse_map_lines.
    if debug:
        print(f"[DEBUG] load_map_text: {len(text)} chars, {len(text.splitlines())} lines")
    raw_lines = [line.rstrip() for line in text.splitlines()]
    result = _parse_map_lines(raw_lines, source="<text>")
    if debug:
        print(f"[DEBUG] load_map_text -> dungeon={result[0]!r}, {result[1]} floor(s) declared, {len(result[2])} loaded")
    return result


def _validate_floor_block(lines: list[str]) -> list[str]:
    """Validate one floor block and return a list of error strings (empty if valid)."""
    # Mirrors _parse_floor_block's structure but collects all errors instead of raising on the first.
    if debug:
        print(f"[DEBUG] _validate_floor_block: {len(lines)} lines")
    errors: list[str] = []

    if not lines:
        if debug:
            print("[DEBUG] _validate_floor_block -> empty block error")
        return ["Empty floor block"]

    try:
        size = int(lines[0].strip())
    except ValueError:
        if debug:
            print(f"[DEBUG] _validate_floor_block -> bad size line: {lines[0]!r}")
        return [f"Size line must be an integer, got: {lines[0]!r}"]

    if size <= 0:
        if debug:
            print(f"[DEBUG] _validate_floor_block -> non-positive size: {size}")
        return ["Size must be a positive integer"]

    if debug:
        print(f"[DEBUG] _validate_floor_block: size={size}, expecting {1 + size + 2} lines, got {len(lines)}")

    expected_lines = 1 + size + 2
    if len(lines) < expected_lines:
        errors.append(
            f"Expected at least {expected_lines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    parsed_rows: list[list[int]] = []
    for i in range(min(size, len(lines) - 1)):
        try:
            parsed_rows.append(parse_row(lines[i + 1], size))
        except ValueError as exc:
            errors.append(f"Row {i + 1}: {exc}")

    grid: list[list[int]] | None = parsed_rows[::-1] if len(parsed_rows) == size else None
    if debug:
        if grid is not None:
            print(f"[DEBUG] _validate_floor_block: grid after reversal (y=0 at bottom):")
            for y, row in enumerate(grid):
                print(f"  y={y}: {row}")
        else:
            print(f"[DEBUG] _validate_floor_block: grid incomplete ({len(parsed_rows)}/{size} rows parsed)")

    player_pos: tuple[int, int] | None = None
    if len(lines) > 1 + size:
        try:
            player_pos = parse_player_line(lines[1 + size], size)
        except ValueError as exc:
            errors.append(f"Player position: {exc}")

    if len(lines) > 2 + size:
        try:
            parse_facing_line(lines[2 + size])
        except ValueError as exc:
            errors.append(f"Facing direction: {exc}")

    if grid is not None and player_pos is not None:
        px, py = player_pos
        if grid[py][px] != 0:
            errors.append(f"Player start ({px}, {py}) is on a blocked tile")

    object_lines = lines[3 + size:]
    if debug:
        print(f"[DEBUG] _validate_floor_block: {len(object_lines)} object descriptor line(s) to validate")
    for j, obj_line in enumerate(object_lines, start=1):
        if debug:
            print(f"[DEBUG] _validate_floor_block: object line {j}: {obj_line!r}")
        if obj_line.startswith("ENEMY|"):
            try:
                enemy = _parse_enemy_line(obj_line, size)
                ex, ey = enemy.grid_x, enemy.grid_y
                if grid is not None and grid[ey][ex] != 0:
                    errors.append(f"Object line {j}: ENEMY {enemy.name!r} position ({ex}, {ey}) is on a blocked tile")
            except ValueError as exc:
                errors.append(f"Object line {j}: {exc}")
        elif obj_line.startswith("ITEM|"):
            try:
                item = _parse_item_line(obj_line, size)
                ix, iy = item.grid_x, item.grid_y
                if grid is not None and grid[iy][ix] != 0:
                    errors.append(f"Object line {j}: ITEM {item.name!r} position ({ix}, {iy}) is on a blocked tile")
            except ValueError as exc:
                errors.append(f"Object line {j}: {exc}")
        elif obj_line.startswith("STAIRS|"):
            parts = obj_line.split("|")
            if len(parts) != 2:
                errors.append(f"Object line {j}: STAIRS line must be 'STAIRS|x y', got: {obj_line!r}")
            else:
                pos_parts = parts[1].strip().split()
                if len(pos_parts) != 2:
                    errors.append(f"Object line {j}: STAIRS position must be 'x y', got: {parts[1]!r}")
                else:
                    try:
                        sx, sy = int(pos_parts[0]), int(pos_parts[1])
                        if not (0 <= sx < size and 0 <= sy < size):
                            errors.append(f"Object line {j}: STAIRS position ({sx}, {sy}) out of bounds for map size {size}")
                        elif grid is not None and grid[sy][sx] != 0:
                            errors.append(f"Object line {j}: STAIRS position ({sx}, {sy}) is on a blocked tile")
                    except ValueError:
                        errors.append(f"Object line {j}: STAIRS position coordinates must be integers: {parts[1]!r}")
        else:
            errors.append(f"Object line {j}: unrecognised descriptor {obj_line!r}")

    if debug:
        print(f"[DEBUG] _validate_floor_block -> {len(errors)} error(s): {errors}")
    return errors


def validate_map_file(path: str | Path) -> tuple[bool, list[str]]:
    """Check that a map file is correctly formatted without loading it for use.

    Returns:
        (is_valid, errors): is_valid is True when no errors were found;
                            errors is a list of human-readable problem descriptions.
    """
    # Entry point for validation; reads from disk and checks the full file format without loading it for use.
    if debug:
        print(f"[DEBUG] validate_map_file: path={str(path)!r}")
    errors: list[str] = []
    path_obj = Path(path)

    try:
        raw_lines = [line.rstrip() for line in path_obj.read_text(encoding="utf-8").splitlines()]
    except FileNotFoundError:
        if debug:
            print(f"[DEBUG] validate_map_file -> file not found: {path_obj}")
        return False, [f"File not found: {path_obj}"]
    except OSError as exc:
        if debug:
            print(f"[DEBUG] validate_map_file -> OS error: {exc}")
        return False, [f"Could not read file: {exc}"]

    if debug:
        print(f"[DEBUG] validate_map_file: read {len(raw_lines)} lines")

    non_empty = [l for l in raw_lines if l.strip() != ""]

    if len(non_empty) < 2:
        return False, ["File too short: missing dungeon name and/or floor count"]

    num_floors: int | None = None
    try:
        num_floors = int(non_empty[1].strip())
        if num_floors <= 0:
            errors.append("Number of floors must be a positive integer")
            num_floors = None
    except ValueError:
        errors.append(f"Second line must be the floor count integer, got: {non_empty[1]!r}")

    if debug:
        print(f"[DEBUG] validate_map_file: name={non_empty[0].strip()!r}, num_floors={num_floors}")

    header_count = 0
    after_header_start = len(raw_lines)
    for i, line in enumerate(raw_lines):
        if line.strip() != "":
            header_count += 1
            if header_count == 2:
                after_header_start = i + 1
                break

    floor_blocks = _split_floor_blocks(raw_lines[after_header_start:])

    if not floor_blocks:
        errors.append("No floor data found")
        if debug:
            print("[DEBUG] validate_map_file -> no floor blocks found")
        return False, errors

    if num_floors is not None and len(floor_blocks) > num_floors:
        errors.append(
            f"File contains {len(floor_blocks)} floor definitions but header declares {num_floors}"
        )

    for i, block in enumerate(floor_blocks):
        if debug:
            print(f"[DEBUG] validate_map_file: validating floor block {i + 1}/{len(floor_blocks)}")
        for e in _validate_floor_block(block):
            errors.append(f"Floor {i + 1}: {e}")

    if debug:
        print(f"[DEBUG] validate_map_file -> valid={len(errors) == 0}, {len(errors)} error(s)")
    return len(errors) == 0, errors


# When the module is run directly, print the loaded dungeon info from a given file path.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load a WizDrive dungeon map file.")
    parser.add_argument("path", help="Path to the map file")
    args = parser.parse_args()

    dungeon_name, num_floors, floors = load_map_file(args.path)
    print(f"Dungeon: {dungeon_name!r}  ({len(floors)}/{num_floors} floors defined)")
    for f, (grid, player_pos, facing, enemies, items, stairs) in enumerate(floors, start=1):
        print(f"\n--- Floor {f} ---")
        print(f"  Grid: {len(grid)} x {len(grid)}")
        print(f"  Player start: {player_pos}, facing={facing}")
        print("  Grid rows (y=0 bottom):")
        for y, row in enumerate(grid):
            print(f"    y={y}: {row}")
        if enemies:
            print("  Enemies:")
            for e in enemies:
                print(f"    {e.name} — hp={e.hp}, attack={e.attack}, speed={e.speed}, pos=({e.grid_x},{e.grid_y})")
        if items:
            print("  Items:")
            for it in items:
                print(f"    {it.name} (value={it.value}) — {it.description}")
        if stairs:
            print(f"  Stairs: {stairs}")