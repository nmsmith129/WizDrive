"""Map loader for WizDrive.

Map file format:
- Line 1: dungeon name
- Line 2: number of floors N (positive integer)
- Then up to N floor blocks, separated by blank lines. Each block contains:
    - One line: grid size S (map is S x S)
    - Next S lines: rows of 0/1 values (first row listed is the bottom of the map)
    - Next line: player x y starting coordinates
    - Next line: initial facing (N/E/S/W or north/east/south/west)

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

# (grid, playerPosition, facing) for one floor
FloorData = tuple[List[List[int]], Tuple[int, int], str]


def parseRow(rowText: str, size: int) -> List[int]:
    values = [token for token in rowText.strip().split() if token != ""]
    if len(values) != size:
        raise ValueError(f"Expected {size} values in row, got {len(values)}: {rowText!r}")

    row = []
    for token in values:
        if token not in {"0", "1"}:
            raise ValueError(f"Map row values must be 0 or 1: {token!r}")
        row.append(int(token))
    return row


def parsePlayerLine(line: str, mapSize: int) -> Tuple[int, int]:
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

    return x, y


def parseFacingLine(line: str) -> str:
    facingToken = line.strip().lower()
    if facingToken not in FACING_MAP:
        raise ValueError(
            f"Facing must be one of N, E, S, W or north/east/south/west: {line!r}"
        )
    return FACING_MAP[facingToken]


def _splitFloorBlocks(lines: list[str]) -> list[list[str]]:
    """Split lines into floor blocks using blank lines as separators."""
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
    return blocks


def _parseFloorBlock(lines: list[str]) -> FloorData:
    """Parse one floor block (size, rows, player, facing) and return its data."""
    if not lines:
        raise ValueError("Empty floor block")

    try:
        size = int(lines[0].strip())
    except ValueError:
        raise ValueError(f"Size line must be an integer, got: {lines[0]!r}")

    if size <= 0:
        raise ValueError("Floor size must be a positive integer")

    expectedLines = 1 + size + 2
    if len(lines) != expectedLines:
        raise ValueError(
            f"Expected {expectedLines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    rawRows = [parseRow(lines[i + 1], size) for i in range(size)]
    grid = rawRows[::-1]
    playerX, playerY = parsePlayerLine(lines[1 + size], size)
    facing = parseFacingLine(lines[2 + size])

    if grid[playerY][playerX] != 0:
        raise ValueError(f"Player start ({playerX}, {playerY}) is on a blocked tile")

    return grid, (playerX, playerY), facing


def _parseMapLines(rawLines: list[str], source: str) -> tuple[str, int, list[FloorData]]:
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
        try:
            floors.append(_parseFloorBlock(block))
        except ValueError as exc:
            raise ValueError(f"Floor {i + 1}: {exc}") from exc

    return name, numFloors, floors


def loadMapFile(path: str | Path) -> tuple[str, int, list[FloorData]]:
    """Load a dungeon from a file.

    Returns:
        name: dungeon name.
        numFloors: total number of floors declared in the header.
        floors: list of (grid, playerPosition, facing) for each floor defined.
                grid[y][x] is the tile at (x, y) with y=0 at the bottom.
    """
    pathObj = Path(path)
    rawLines = [line.rstrip() for line in pathObj.read_text(encoding="utf-8").splitlines()]
    return _parseMapLines(rawLines, source=str(pathObj))


def loadMapText(text: str) -> tuple[str, int, list[FloorData]]:
    """Load dungeon data from a string using the same format as loadMapFile."""
    rawLines = [line.rstrip() for line in text.splitlines()]
    return _parseMapLines(rawLines, source="<text>")


def _validateFloorBlock(lines: list[str]) -> list[str]:
    """Validate one floor block and return a list of error strings (empty if valid)."""
    errors: list[str] = []

    if not lines:
        return ["Empty floor block"]

    try:
        size = int(lines[0].strip())
    except ValueError:
        return [f"Size line must be an integer, got: {lines[0]!r}"]

    if size <= 0:
        return ["Size must be a positive integer"]

    expectedLines = 1 + size + 2
    if len(lines) != expectedLines:
        errors.append(
            f"Expected {expectedLines} lines (1 size + {size} rows + player + facing), "
            f"got {len(lines)}"
        )

    parsedRows: list[list[int]] = []
    for i in range(min(size, len(lines) - 1)):
        try:
            parsedRows.append(parseRow(lines[i + 1], size))
        except ValueError as exc:
            errors.append(f"Row {i + 1}: {exc}")

    grid: list[list[int]] | None = parsedRows[::-1] if len(parsedRows) == size else None

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

    return errors


def validateMapFile(path: str | Path) -> tuple[bool, list[str]]:
    """Check that a map file is correctly formatted without loading it for use.

    Returns:
        (is_valid, errors): is_valid is True when no errors were found;
                            errors is a list of human-readable problem descriptions.
    """
    errors: list[str] = []
    pathObj = Path(path)

    try:
        rawLines = [line.rstrip() for line in pathObj.read_text(encoding="utf-8").splitlines()]
    except FileNotFoundError:
        return False, [f"File not found: {pathObj}"]
    except OSError as exc:
        return False, [f"Could not read file: {exc}"]

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
        return False, errors

    if numFloors is not None and len(floorBlocks) > numFloors:
        errors.append(
            f"File contains {len(floorBlocks)} floor definitions but header declares {numFloors}"
        )

    for i, block in enumerate(floorBlocks):
        for e in _validateFloorBlock(block):
            errors.append(f"Floor {i + 1}: {e}")

    return len(errors) == 0, errors


# When the module is run directly, print the loaded dungeon info from a given file path.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load a WizDrive dungeon map file.")
    parser.add_argument("path", help="Path to the map file")
    args = parser.parse_args()

    dungeonName, numFloors, floors = loadMapFile(args.path)
    print(f"Dungeon: {dungeonName!r}  ({len(floors)}/{numFloors} floors defined)")
    for f, (grid, playerPos, facing) in enumerate(floors, start=1):
        print(f"\n--- Floor {f} ---")
        print(f"  Grid: {len(grid)} x {len(grid)}")
        print(f"  Player start: {playerPos}, facing={facing}")
        print("  Grid rows (y=0 bottom):")
        for y, row in enumerate(grid):
            print(f"    y={y}: {row}")