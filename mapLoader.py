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

# (grid, playerPosition, facing) for one floor
FloorData = tuple[List[List[int]], Tuple[int, int], str]


def parseRow(rowText: str, size: int) -> List[int]:
    if debug:
        print(f"[DEBUG] parseRow: rowText={rowText!r}, size={size}")
    values = [token for token in rowText.strip().split() if token != ""]
    if len(values) != size:
        raise ValueError(f"Expected {size} values in row, got {len(values)}: {rowText!r}")

    row = []
    for token in values:
        if token not in {"0", "1"}:
            raise ValueError(f"Map row values must be 0 or 1: {token!r}")
        row.append(int(token))
    if debug:
        print(f"[DEBUG] parseRow -> {row}")
    return row


def parsePlayerLine(line: str, mapSize: int) -> Tuple[int, int]:
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


def _splitFloorBlocks(lines: list[str]) -> list[list[str]]:
    """Split lines into floor blocks using blank lines as separators."""
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
    if len(lines) != expectedLines:
        raise ValueError(
            f"Expected {expectedLines} lines (1 size + {size} rows + player + facing), "
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

    if debug:
        print(f"[DEBUG] _parseFloorBlock -> {size}x{size} grid, player=({playerX},{playerY}), facing={facing!r}")
        print(f"[DEBUG] _parseFloorBlock: grid with player marked (P):")
        for y, row in enumerate(grid):
            displayed = [("P" if (xi == playerX and y == playerY) else str(v)) for xi, v in enumerate(row)]
            print(f"  y={y}: [{', '.join(displayed)}]")
    return grid, (playerX, playerY), facing


def _parseMapLines(rawLines: list[str], source: str) -> tuple[str, int, list[FloorData]]:
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
    if debug:
        print(f"[DEBUG] loadMapText: {len(text)} chars, {len(text.splitlines())} lines")
    rawLines = [line.rstrip() for line in text.splitlines()]
    result = _parseMapLines(rawLines, source="<text>")
    if debug:
        print(f"[DEBUG] loadMapText -> dungeon={result[0]!r}, {result[1]} floor(s) declared, {len(result[2])} loaded")
    return result


def _validateFloorBlock(lines: list[str]) -> list[str]:
    """Validate one floor block and return a list of error strings (empty if valid)."""
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

    if debug:
        print(f"[DEBUG] _validateFloorBlock -> {len(errors)} error(s): {errors}")
    return errors


def validateMapFile(path: str | Path) -> tuple[bool, list[str]]:
    """Check that a map file is correctly formatted without loading it for use.

    Returns:
        (is_valid, errors): is_valid is True when no errors were found;
                            errors is a list of human-readable problem descriptions.
    """
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
    for f, (grid, playerPos, facing) in enumerate(floors, start=1):
        print(f"\n--- Floor {f} ---")
        print(f"  Grid: {len(grid)} x {len(grid)}")
        print(f"  Player start: {playerPos}, facing={facing}")
        print("  Grid rows (y=0 bottom):")
        for y, row in enumerate(grid):
            print(f"    y={y}: {row}")