from __future__ import annotations

from enum import IntFlag


class Direction(IntFlag):
    """A wall side. The integer value is the bit used in the file encoding."""
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> Direction:
        """the same wall seen from the neighbour cell"""
        return OPPOSITE[self]

    @property
    def step(self) -> tuple[int, int]:
        """the (row, col) offset to the neihbour on  this side"""
        return STEP[self]


OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST
}


STEP: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (-1, 0),
    Direction.EAST: (0, 1),
    Direction.SOUTH: (1, 0),
    Direction.WEST: (0, -1)
}

WALLS = Direction.NORTH | Direction.EAST | Direction.SOUTH | Direction.WEST


class Cell:
    "Represents a single cell in grid of maze"
    def __init__(self, row: int, col: int):
        self.row: int = row
        self.col: int = col
        self.walls: Direction = WALLS
        self.visited: bool = False
        self.is_42: bool = False
