from __future__ import annotations

from random import randint, seed, shuffle
from typing import Final

from .cell import Cell, Direction


class MazeError(Exception):
    """Exception raised when maze generation fails."""


class MazeGenerator:
    """
    Generate a maze based on validated configuration.
    """

    def __init__(
        self,
        height: int,
        width: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool,
        seeds: int | None,
    ) -> None:
        """
        Initialize the maze generator.

        Args:
            height: Height of the maze.
            width: Width of the maze.
            entry: Row and column coordinates of the entry.
            exit: Row and column coordinates of the exit.
            perfect: Whether to generate a perfect maze.
            seeds: Optional integer seed for random generation.

        Raises:
            MazeError: If entry or exit overlaps the 42 pattern.
        """
        self.height: Final[int] = height
        self.width: Final[int] = width
        self.entry: Final[tuple[int, int]] = entry
        self.exit: Final[tuple[int, int]] = exit
        self.perfect: Final[bool] = perfect
        self.seed: Final[int] = (
            seeds if seeds is not None else randint(0, 1000)
        )

        seed(self.seed)
        self.grid: list[list[Cell]] = self.grid_init()

    def grid_init(self) -> list[list[Cell]]:
        """
        Initialize the maze grid and place the 42 pattern.

        Create a grid of cells based on the maze dimensions.
        Place the 42 pattern in the center when both dimensions
        are large enough to contain the pattern.

        Returns:
            A two-dimensional list containing maze cells.

        Raises:
            MazeError: If entry or exit overlaps the 42 pattern.
        """
        grid: list[list[Cell]] = []

        for row in range(self.height):
            current_row: list[Cell] = []

            for col in range(self.width):
                current_row.append(Cell(row, col))

            grid.append(current_row)

        pattern_42: list[tuple[int, int]] = [
            (0, 0), (1, 0), (2, 0), (2, 1),
            (2, 2), (3, 2), (4, 2),
            (0, 4), (0, 5), (0, 6), (1, 6),
            (2, 6), (2, 5), (2, 4), (3, 4),
            (4, 4), (4, 5), (4, 6),
        ]

        pattern_height = 5
        pattern_width = 7

        if (
            self.height < pattern_height
            or self.width < pattern_width
        ):
            print(
                "Height or width is too small for the 42 pattern. "
                "Omitting the pattern."
            )
            return grid

        start_row = (self.height - pattern_height) // 2
        start_col = (self.width - pattern_width) // 2

        for pattern_row, pattern_col in pattern_42:
            maze_row = pattern_row + start_row
            maze_col = pattern_col + start_col

            if (
                (self.entry == (maze_row, maze_col))
                or (self.exit == (maze_row, maze_col))
            ):
                raise MazeError(
                    "Entry and exit must not overlap the 42 pattern."
                )

            grid[maze_row][maze_col].is_42 = True

        return grid

    def dfs(self, cell: Cell) -> None:
        """
        Generate maze passages using depth-first search.

        Visit neighboring cells recursively and remove the walls
        between connected cells. Cells belonging to the 42 pattern
        are excluded from maze generation.

        Args:
            cell: Cell from which the search begins.

        Returns:
            None.
        """
        current_cell = self.grid[cell.row][cell.col]
        current_cell.visited = True

        directions: list[Direction] = list(Direction)
        shuffle(directions)

        for direction in directions:
            new_row = current_cell.row + direction.step[0]
            new_col = current_cell.col + direction.step[1]

            if not 0 <= new_row < self.height:
                continue

            if not 0 <= new_col < self.width:
                continue

            neighbor = self.grid[new_row][new_col]

            if not neighbor.visited and not neighbor.is_42:
                current_cell.walls &= ~direction
                neighbor.walls &= ~direction.opposite

                self.dfs(neighbor)

    def count_open_walls(self, cell: Cell) -> int:
        """
        Count the open walls around a cell.

        Args:
            cell: Maze cell to check.

        Returns:
            Number of open walls around the cell.
        """
        count = 0

        for direction in Direction:
            if not (cell.walls & direction):
                count += 1

        return count

    def add_loops(self) -> None:
        """
        Add additional passages to the maze.

        Find dead-end cells and remove a wall to create additional
        connections. Cells belonging to the 42 pattern are excluded.

        Returns:
            None.
        """
        cells: list[Cell] = []

        for row in self.grid:
            for cell in row:
                if not cell.is_42:
                    cells.append(cell)

        shuffle(cells)

        while True:
            dead_end_found = False

            for cell in cells:
                if self.count_open_walls(cell) != 1:
                    continue

                directions: list[Direction] = list(Direction)
                shuffle(directions)

                for direction in directions:
                    new_row = cell.row + direction.step[0]
                    new_col = cell.col + direction.step[1]

                    if not 0 <= new_row < self.height:
                        continue

                    if not 0 <= new_col < self.width:
                        continue

                    neighbor = self.grid[new_row][new_col]

                    if (
                        not neighbor.is_42
                        and cell.walls & direction
                    ):
                        cell.walls &= ~direction
                        neighbor.walls &= ~direction.opposite

                        dead_end_found = True
                        break

                if dead_end_found:
                    break

            if not dead_end_found:
                break

    def generate_maze(self) -> None:
        """
        Generate the maze using the selected generation mode.

        Use depth-first search to generate passages. If the maze
        is not required to be perfect, add additional passages
        to create loops.

        Returns:
            None.
        """
        start_cell = self.grid[self.entry[0]][self.entry[1]]

        self.dfs(start_cell)

        if not self.perfect:
            self.add_loops()
