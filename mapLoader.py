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
        ENEMY|name|hp|attack|speed|x y
        ITEM|name|value|description|x y

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
ENEMY|Goblin|10|3|2|4 3
ITEM|Gold Coin|5|A shiny gold coin|6 3

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
from typing import List, Tuple

from enemy import Enemy
from enemyTypes import get_stats
from item import Item

debug = True  # set to True to enable diagnostic output

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

FloorData = tuple[List[List[int]], Tuple[int, int], str, List[Enemy], List[Item], Tuple[int, int] | None]


def parseRow(rowText: str, size: int) -> List[int]:
    # Parses one grid row from the "Next S lines" section of a floor block; each token must be 0 or 1.
    if debug:
        print(f"[DEBUG] parseRow: rowText={rowText!r}, size={size}")
    # Split on any whitespace and drop empty strings to handle irregular spacing.
    values = [token for token in rowText.strip().split() if token != ""]
    # Enforce that each row has exactly `size` tiles to match the declared grid width.
    if len(values) != size:
        raise ValueError(f"Expected {size} values in row, got {len(values)}: {rowText!r}")

    row = []
    for token in values:
        # Only 0 (open tile) and 1 (wall) are valid map values.
        if token not in {"0", "1"}:
            raise ValueError(f"Map row values must be 0 or 1: {token!r}")
        row.append(int(token))
    if debug:
        print(f"[DEBUG] parseRow -> {row}")
    return row


def parsePlayerLine(line: str, mapSize: int) -> Tuple[int, int]:
    # Parses the "player x y" line that immediately follows the S grid rows in a floor block.
    if debug:
        print(f"[DEBUG] parsePlayerLine: line={line!r}, mapSize={mapSize}")
    tokens = [token for token in line.strip().split() if token != ""]
    if len(tokens) != 2:
        raise ValueError(f"Player position line must contain exactly two numbers: {line!r}")

    try:
        x = int(tokens[0])
        y = int(tokens[1])
    except ValueError as exc:
        raise ValueError(f"Player coordinates must be integers: {line!r}") from exc

    if not (0 <= x < mapSize and 0 <= y < mapSize):
        raise ValueError(f"Player coordinates out of bounds: ({x}, {y}) for map size {mapSize}")

    if debug:
        print(f"[DEBUG] parsePlayerLine -> ({x}, {y})")
    return x, y


def parseFacingLine(line: str) -> str:
    # Parses the facing direction line (N/E/S/W or full word) that follows the player position line.
    if debug:
        print(f"[DEBUG] parseFacingLine: line={line!r}")
    facingToken = line.strip().lower()
    if facingToken not in FACING_MAP:
        raise ValueError(
            f"Facing must be one of N, E, S, W or north/east/south/west: {line!r}"
        )
    result = FACING_MAP[facingToken]
    if debug:
        print(f"[DEBUG] parseFacingLine -> {result!r}")
    return result


def _parseEnemyLine(line: str, mapSize: int) -> Enemy:
    # Parses ENEMY|name|x y (stats from library) or ENEMY|name|hp|attack|speed|x y (explicit stats).
    if debug:
        print(f"[DEBUG] _parseEnemyLine: line={line!r}, mapSize={mapSize}")
    parts = line.split("|")
    if len(parts) == 3:
        _, name, rawPos = parts
        if not name.strip():
            raise ValueError(f"ENEMY name must not be empty: {line!r}")
        stats = get_stats(name.strip())
        hp, attack, speed = stats["hp"], stats["attack"], stats["speed"]
    elif len(parts) == 6:
        _, name, rawHp, rawAttack, rawSpeed, rawPos = parts
        if not name.strip():
            raise ValueError(f"ENEMY name must not be empty: {line!r}")
        try:
            hp     = int(rawHp)
            attack = int(rawAttack)
            speed  = int(rawSpeed)
        except ValueError:
            raise ValueError(f"ENEMY hp/attack/speed must be integers: {line!r}")
        if hp <= 0 or attack <= 0 or speed <= 0:
            raise ValueError(f"ENEMY hp/attack/speed must be positive: {line!r}")
    else:
        raise ValueError(f"ENEMY line must have 3 or 6 pipe-separated fields, got {len(parts)}: {line!r}")
    posParts = rawPos.strip().split()
    if len(posParts) != 2:
        raise ValueError(f"ENEMY position must be 'x y', got: {rawPos!r}")
    try:
        x, y = int(posParts[0]), int(posParts[1])
    except ValueError:
        raise ValueError(f"ENEMY position coordinates must be integers: {rawPos!r}")
    if not (0 <= x < mapSize and 0 <= y < mapSize):
        raise ValueError(f"ENEMY position ({x}, {y}) out of bounds for map size {mapSize}")
    if debug:
        print(f"[DEBUG] _parseEnemyLine -> parsed fields: name={name!r}, hp={hp}, attack={attack}, speed={speed}, pos=({x},{y})")
    enemy = Enemy(name.strip(), hp, attack, speed, x, y)
    if debug:
        print(f"[DEBUG] _parseEnemyLine -> Enemy object created:")
        print(f"  .name={enemy.name!r}, .hp={enemy.hp}, .attack={enemy.attack}, .speed={enemy.speed}")
        print(f"  .grid_x={enemy.grid_x}, .grid_y={enemy.grid_y}")
        print(f"  .image={enemy.image}, size={enemy.image.get_size()}")
        print(f"  .rect={enemy.rect}")
        ok = (
            enemy.name == name.strip()
            and enemy.hp == hp
            and enemy.attack == attack
            and enemy.speed == speed
            and enemy.grid_x == x
            and enemy.grid_y == y
        )
        print(f"[DEBUG] _parseEnemyLine -> data integrity check: {'PASS' if ok else 'FAIL'}")
    return enemy


def _parseItemLine(line: str, mapSize: int) -> Item:
    # Parses one ITEM|name|value|description|x y descriptor from the object section of a floor block.
    if debug:
        print(f"[DEBUG] _parseItemLine: line={line!r}, mapSize={mapSize}")
    parts = line.split("|")
    if len(parts) != 5:
        raise ValueError(f"ITEM line must have 5 pipe-separated fields, got {len(parts)}: {line!r}")
    _, name, rawValue, description, rawPos = parts
    if not name.strip():
        raise ValueError(f"ITEM name must not be empty: {line!r}")
    try:
        value = int(rawValue)
    except ValueError:
        raise ValueError(f"ITEM value must be an integer: {line!r}")
    if value <= 0:
        raise ValueError(f"ITEM value must be positive: {line!r}")
    posParts = rawPos.strip().split()
    if len(posParts) != 2:
        raise ValueError(f"ITEM position must be 'x y', got: {rawPos!r}")
    try:
        x, y = int(posParts[0]), int(posParts[1])
    except ValueError:
        raise ValueError(f"ITEM position coordinates must be integers: {rawPos!r}")
    if not (0 <= x < mapSize and 0 <= y < mapSize):
        raise ValueError(f"ITEM position ({x}, {y}) out of bounds for map size {mapSize}")
    if debug:
        print(f"[DEBUG] _parseItemLine -> parsed fields: name={name!r}, value={value}, description={description!r}, pos=({x},{y})")
    item = Item(name.strip(), value, description.strip(), x, y)
    if debug:
        print(f"[DEBUG] _parseItemLine -> Item object created:")
        print(f"  .name={item.name!r}, .value={item.value}, .description={item.description!r}")
        print(f"  .grid_x={item.grid_x}, .grid_y={item.grid_y}")
        print(f"  .image={item.image}, size={item.image.get_size()}")
        print(f"  .rect={item.rect}")
        ok = (
            item.name == name.strip()
            and item.value == value
            and item.description == description.strip()
            and item.grid_x == x
            and item.grid_y == y
        )
        print(f"[DEBUG] _parseItemLine -> data integrity check: {'PASS' if ok else 'FAIL'}")
    return item


def _splitFloorBlocks(lines: list[str]) -> list[list[str]]:
    """Split lines into floor blocks using blank lines as separators."""
    # Receives all raw lines after the two-line header (dungeon name + floor count).
    if debug:
        print(f"[DEBUG] _splitFloorBlocks: {len(lines)} input lines")
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
        print(f"[DEBUG] _splitFloorBlocks -> {len(blocks)} block(s), sizes={[len(b) for b in blocks]}")
    return blocks


def _parseFloorBlock(lines: list[str]) -> FloorData:
    """Parse one floor block (size, rows, player, facing) and return its data."""
    # Covers: size line, S grid rows, player position, facing direction, and ENEMY/ITEM descriptor lines.
    if debug:
        print(f"[DEBUG] _parseFloorBlock: {len(lines)} lines, first={repr(lines[0]) if lines else 'N/A'}")
    if not lines:
        raise ValueError("Empty floor block")

    try:
        size = int(lines[0].strip())
    except ValueError:
        raise ValueError(f"Size line must be an integer, got: {lines[0]!r}")

    if size <= 0:
        raise ValueError("Floor size must be a positive integer")

    if debug:
        print(f"[DEBUG] _parseFloorBlock: size={size}, expecting {1 + size + 2} lines, got {len(lines)}")

    expectedLines = 1 + size + 2
    if len(lines) < expectedLines:
        raise ValueError(
            f"Expected at least {expectedLines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    rawRows = [parseRow(lines[i + 1], size) for i in range(size)]
    grid = rawRows[::-1]
    if debug:
        print(f"[DEBUG] _parseFloorBlock: rawRows (top-to-bottom as in file):")
        for i, row in enumerate(rawRows):
            print(f"  file row {i}: {row}")
        print(f"[DEBUG] _parseFloorBlock: grid after reversal (y=0 at bottom):")
        for y, row in enumerate(grid):
            print(f"  y={y}: {row}")
    playerX, playerY = parsePlayerLine(lines[1 + size], size)
    facing = parseFacingLine(lines[2 + size])

    if grid[playerY][playerX] != 0:
        raise ValueError(f"Player start ({playerX}, {playerY}) is on a blocked tile")

    enemies: List[Enemy] = []
    items: List[Item] = []
    stairs: Tuple[int, int] | None = None
    for j, objLine in enumerate(lines[3 + size:], start=1):
        if objLine.startswith("ENEMY|"):
            enemy = _parseEnemyLine(objLine, size)
            ex, ey = enemy.grid_x, enemy.grid_y
            if grid[ey][ex] != 0:
                raise ValueError(f"Object line {j}: ENEMY {enemy.name!r} position ({ex}, {ey}) is on a blocked tile")
            enemies.append(enemy)
        elif objLine.startswith("ITEM|"):
            item = _parseItemLine(objLine, size)
            ix, iy = item.grid_x, item.grid_y
            if grid[iy][ix] != 0:
                raise ValueError(f"Object line {j}: ITEM {item.name!r} position ({ix}, {iy}) is on a blocked tile")
            items.append(item)
        elif objLine.startswith("STAIRS|"):
            parts = objLine.split("|")
            if len(parts) != 2:
                raise ValueError(f"STAIRS line must be 'STAIRS|x y', got: {objLine!r}")
            posParts = parts[1].strip().split()
            if len(posParts) != 2:
                raise ValueError(f"STAIRS position must be 'x y', got: {parts[1]!r}")
            sx, sy = int(posParts[0]), int(posParts[1])
            if not (0 <= sx < size and 0 <= sy < size):
                raise ValueError(f"STAIRS position ({sx}, {sy}) out of bounds for map size {size}")
            if grid[sy][sx] != 0:
                raise ValueError(f"STAIRS position ({sx}, {sy}) is on a blocked tile")
            stairs = (sx, sy)
        else:
            raise ValueError(f"Object line {j}: unrecognised descriptor {objLine!r}")

    if debug:
        print(f"[DEBUG] _parseFloorBlock -> {size}x{size} grid, player=({playerX},{playerY}), facing={facing!r}, {len(enemies)} enemy/enemies, {len(items)} item(s)")
        print(f"[DEBUG] _parseFloorBlock: grid with player marked (P):")
        for y, row in enumerate(grid):
            displayed = [("P" if (xi == playerX and y == playerY) else str(v)) for xi, v in enumerate(row)]
            print(f"  y={y}: [{', '.join(displayed)}]")
        for e in enemies:
            print(f"  enemy: {e.name} hp={e.hp} attack={e.attack} speed={e.speed} pos=({e.grid_x},{e.grid_y})")
        for it in items:
            print(f"  item:  {it.name} value={it.value} desc={it.description!r}")
    return grid, (playerX, playerY), facing, enemies, items, stairs


def _parseMapLines(rawLines: list[str], source: str) -> tuple[str, int, list[FloorData]]:
    # Reads the two-line header (dungeon name + floor count), then parses each floor block in sequence.
    if debug:
        print(f"[DEBUG] _parseMapLines: source={source!r}, {len(rawLines)} raw lines")
    nonEmpty = [l for l in rawLines if l.strip() != ""]
    if len(nonEmpty) < 2:
        raise ValueError(f"'{source}' is too short: missing dungeon name or floor count")

    name = nonEmpty[0].strip()

    try:
        numFloors = int(nonEmpty[1].strip())
    except ValueError:
        raise ValueError(f"Second line must be the floor count integer, got: {nonEmpty[1]!r}")

    if numFloors <= 0:
        raise ValueError("Number of floors must be a positive integer")

    if debug:
        print(f"[DEBUG] _parseMapLines: name={name!r}, numFloors={numFloors}")

    # Find the index in rawLines immediately after the second non-empty line.
    headerCount = 0
    afterHeaderStart = len(rawLines)
    for i, line in enumerate(rawLines):
        if line.strip() != "":
            headerCount += 1
            if headerCount == 2:
                afterHeaderStart = i + 1
                break

    floorBlocks = _splitFloorBlocks(rawLines[afterHeaderStart:])

    if not floorBlocks:
        raise ValueError(f"No floor data found in '{source}'")

    if len(floorBlocks) > numFloors:
        raise ValueError(
            f"'{source}' contains {len(floorBlocks)} floor definitions but header declares {numFloors}"
        )

    floors: list[FloorData] = []
    for i, block in enumerate(floorBlocks):
        if debug:
            print(f"[DEBUG] _parseMapLines: parsing floor block {i + 1}/{len(floorBlocks)}")
        try:
            floors.append(_parseFloorBlock(block))
        except ValueError as exc:
            raise ValueError(f"Floor {i + 1}: {exc}") from exc

    if debug:
        print(f"[DEBUG] _parseMapLines -> name={name!r}, numFloors={numFloors}, {len(floors)} floor(s) loaded")
    return name, numFloors, floors


def loadMapFile(path: str | Path) -> tuple[str, int, list[FloorData]]:
    """Load a dungeon from a file.

    Returns:
        name: dungeon name.
        numFloors: total number of floors declared in the header.
        floors: list of (grid, playerPosition, facing) for each floor defined.
                grid[y][x] is the tile at (x, y) with y=0 at the bottom.
    """
    # Entry point for dungeon files on disk; enforces .dngn extension before delegating to _parseMapLines.
    if debug:
        print(f"[DEBUG] loadMapFile: path={str(path)!r}")
    pathObj = Path(path)
    if pathObj.suffix != ".dngn":
        raise ValueError(f"Map file must have a .dngn extension, got: {pathObj.name!r}")
    rawLines = [line.rstrip() for line in pathObj.read_text(encoding="utf-8").splitlines()]
    if debug:
        print(f"[DEBUG] loadMapFile: read {len(rawLines)} lines from {str(pathObj)!r}")
    result = _parseMapLines(rawLines, source=str(pathObj))
    if debug:
        print(f"[DEBUG] loadMapFile -> dungeon={result[0]!r}, {result[1]} floor(s) declared, {len(result[2])} loaded")
    return result


def loadMapText(text: str) -> tuple[str, int, list[FloorData]]:
    """Load dungeon data from a string using the same format as loadMapFile."""
    # Entry point for in-memory map text; skips the file-read step and delegates directly to _parseMapLines.
    if debug:
        print(f"[DEBUG] loadMapText: {len(text)} chars, {len(text.splitlines())} lines")
    rawLines = [line.rstrip() for line in text.splitlines()]
    result = _parseMapLines(rawLines, source="<text>")
    if debug:
        print(f"[DEBUG] loadMapText -> dungeon={result[0]!r}, {result[1]} floor(s) declared, {len(result[2])} loaded")
    return result


def _validateFloorBlock(lines: list[str]) -> list[str]:
    """Validate one floor block and return a list of error strings (empty if valid)."""
    # Mirrors _parseFloorBlock's structure but collects all errors instead of raising on the first.
    if debug:
        print(f"[DEBUG] _validateFloorBlock: {len(lines)} lines")
    errors: list[str] = []

    if not lines:
        if debug:
            print("[DEBUG] _validateFloorBlock -> empty block error")
        return ["Empty floor block"]

    try:
        size = int(lines[0].strip())
    except ValueError:
        if debug:
            print(f"[DEBUG] _validateFloorBlock -> bad size line: {lines[0]!r}")
        return [f"Size line must be an integer, got: {lines[0]!r}"]

    if size <= 0:
        if debug:
            print(f"[DEBUG] _validateFloorBlock -> non-positive size: {size}")
        return ["Size must be a positive integer"]

    if debug:
        print(f"[DEBUG] _validateFloorBlock: size={size}, expecting {1 + size + 2} lines, got {len(lines)}")

    expectedLines = 1 + size + 2
    if len(lines) < expectedLines:
        errors.append(
            f"Expected at least {expectedLines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    parsedRows: list[list[int]] = []
    for i in range(min(size, len(lines) - 1)):
        try:
            parsedRows.append(parseRow(lines[i + 1], size))
        except ValueError as exc:
            errors.append(f"Row {i + 1}: {exc}")

    grid: list[list[int]] | None = parsedRows[::-1] if len(parsedRows) == size else None
    if debug:
        if grid is not None:
            print(f"[DEBUG] _validateFloorBlock: grid after reversal (y=0 at bottom):")
            for y, row in enumerate(grid):
                print(f"  y={y}: {row}")
        else:
            print(f"[DEBUG] _validateFloorBlock: grid incomplete ({len(parsedRows)}/{size} rows parsed)")

    playerPos: tuple[int, int] | None = None
    if len(lines) > 1 + size:
        try:
            playerPos = parsePlayerLine(lines[1 + size], size)
        except ValueError as exc:
            errors.append(f"Player position: {exc}")

    if len(lines) > 2 + size:
        try:
            parseFacingLine(lines[2 + size])
        except ValueError as exc:
            errors.append(f"Facing direction: {exc}")

    if grid is not None and playerPos is not None:
        px, py = playerPos
        if grid[py][px] != 0:
            errors.append(f"Player start ({px}, {py}) is on a blocked tile")

    objectLines = lines[3 + size:]
    if debug:
        print(f"[DEBUG] _validateFloorBlock: {len(objectLines)} object descriptor line(s) to validate")
    for j, objLine in enumerate(objectLines, start=1):
        if debug:
            print(f"[DEBUG] _validateFloorBlock: object line {j}: {objLine!r}")
        if objLine.startswith("ENEMY|"):
            try:
                enemy = _parseEnemyLine(objLine, size)
                ex, ey = enemy.grid_x, enemy.grid_y
                if grid is not None and grid[ey][ex] != 0:
                    errors.append(f"Object line {j}: ENEMY {enemy.name!r} position ({ex}, {ey}) is on a blocked tile")
            except ValueError as exc:
                errors.append(f"Object line {j}: {exc}")
        elif objLine.startswith("ITEM|"):
            try:
                item = _parseItemLine(objLine, size)
                ix, iy = item.grid_x, item.grid_y
                if grid is not None and grid[iy][ix] != 0:
                    errors.append(f"Object line {j}: ITEM {item.name!r} position ({ix}, {iy}) is on a blocked tile")
            except ValueError as exc:
                errors.append(f"Object line {j}: {exc}")
        elif objLine.startswith("STAIRS|"):
            parts = objLine.split("|")
            if len(parts) != 2:
                errors.append(f"Object line {j}: STAIRS line must be 'STAIRS|x y', got: {objLine!r}")
            else:
                posParts = parts[1].strip().split()
                if len(posParts) != 2:
                    errors.append(f"Object line {j}: STAIRS position must be 'x y', got: {parts[1]!r}")
                else:
                    try:
                        sx, sy = int(posParts[0]), int(posParts[1])
                        if not (0 <= sx < size and 0 <= sy < size):
                            errors.append(f"Object line {j}: STAIRS position ({sx}, {sy}) out of bounds for map size {size}")
                        elif grid is not None and grid[sy][sx] != 0:
                            errors.append(f"Object line {j}: STAIRS position ({sx}, {sy}) is on a blocked tile")
                    except ValueError:
                        errors.append(f"Object line {j}: STAIRS position coordinates must be integers: {parts[1]!r}")
        else:
            errors.append(f"Object line {j}: unrecognised descriptor {objLine!r}")

    if debug:
        print(f"[DEBUG] _validateFloorBlock -> {len(errors)} error(s): {errors}")
    return errors


def validateMapFile(path: str | Path) -> tuple[bool, list[str]]:
    """Check that a map file is correctly formatted without loading it for use.

    Returns:
        (is_valid, errors): is_valid is True when no errors were found;
                            errors is a list of human-readable problem descriptions.
    """
    # Entry point for validation; reads from disk and checks the full file format without loading it for use.
    if debug:
        print(f"[DEBUG] validateMapFile: path={str(path)!r}")
    errors: list[str] = []
    pathObj = Path(path)

    try:
        rawLines = [line.rstrip() for line in pathObj.read_text(encoding="utf-8").splitlines()]
    except FileNotFoundError:
        if debug:
            print(f"[DEBUG] validateMapFile -> file not found: {pathObj}")
        return False, [f"File not found: {pathObj}"]
    except OSError as exc:
        if debug:
            print(f"[DEBUG] validateMapFile -> OS error: {exc}")
        return False, [f"Could not read file: {exc}"]

    if debug:
        print(f"[DEBUG] validateMapFile: read {len(rawLines)} lines")

    nonEmpty = [l for l in rawLines if l.strip() != ""]

    if len(nonEmpty) < 2:
        return False, ["File too short: missing dungeon name and/or floor count"]

    numFloors: int | None = None
    try:
        numFloors = int(nonEmpty[1].strip())
        if numFloors <= 0:
            errors.append("Number of floors must be a positive integer")
            numFloors = None
    except ValueError:
        errors.append(f"Second line must be the floor count integer, got: {nonEmpty[1]!r}")

    if debug:
        print(f"[DEBUG] validateMapFile: name={nonEmpty[0].strip()!r}, numFloors={numFloors}")

    headerCount = 0
    afterHeaderStart = len(rawLines)
    for i, line in enumerate(rawLines):
        if line.strip() != "":
            headerCount += 1
            if headerCount == 2:
                afterHeaderStart = i + 1
                break

    floorBlocks = _splitFloorBlocks(rawLines[afterHeaderStart:])

    if not floorBlocks:
        errors.append("No floor data found")
        if debug:
            print("[DEBUG] validateMapFile -> no floor blocks found")
        return False, errors

    if numFloors is not None and len(floorBlocks) > numFloors:
        errors.append(
            f"File contains {len(floorBlocks)} floor definitions but header declares {numFloors}"
        )

    for i, block in enumerate(floorBlocks):
        if debug:
            print(f"[DEBUG] validateMapFile: validating floor block {i + 1}/{len(floorBlocks)}")
        for e in _validateFloorBlock(block):
            errors.append(f"Floor {i + 1}: {e}")

    if debug:
        print(f"[DEBUG] validateMapFile -> valid={len(errors) == 0}, {len(errors)} error(s)")
    return len(errors) == 0, errors


# When the module is run directly, print the loaded dungeon info from a given file path.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load a WizDrive dungeon map file.")
    parser.add_argument("path", help="Path to the map file")
    args = parser.parse_args()

    dungeonName, numFloors, floors = loadMapFile(args.path)
    print(f"Dungeon: {dungeonName!r}  ({len(floors)}/{numFloors} floors defined)")
    for f, (grid, playerPos, facing, enemies, items) in enumerate(floors, start=1):
        print(f"\n--- Floor {f} ---")
        print(f"  Grid: {len(grid)} x {len(grid)}")
        print(f"  Player start: {playerPos}, facing={facing}")
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