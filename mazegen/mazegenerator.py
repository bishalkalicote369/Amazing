from __future__ import annotations

from typing import Final
from random import (
    randint,
    seed,
    shuffle
)
from io_utils import (
    ConfigModel,
    load_config
)
from .cell import (
    Cell,
    Direction,
)


class MazeGenerator:
    """Generate maze based on validated configuration"""
    def __init__(self, config_file: str) -> None:
        self.config: Final[ConfigModel] = load_config(config_file)

        self.height: Final[int] = self.config.HEIGHT
        self.width: Final[int] = self.config.WIDTH
        self.entry: Final[tuple[int, int]] = self.config.ENTRY
        self.exit: Final[tuple[int, int]] = self.config.EXIT
        self.output_file: Final[str] = self.config.OUTPUT_FILE
        self.perfect: Final[bool] = self.config.PERFECT
        self.seed: Final[int | None] = (
            self.config.SEED
            if self.config.SEED is not None
            else randint(0, 1000)
        )
        seed(self.seed)
        self.grid = self.grid_init()

    def grid_init(self):

        grid = []

        for row in range(self.height):
            current_row = []
            for col in range(self.width):
                current_row.append(Cell(row, col))
            grid.append(current_row)

        pattern_42: list[tuple[int, int]] = [
                    (0, 0), (1, 0), (2, 0), (2, 1),
                    (2, 2), (3, 2), (4, 2),  # 4
                    (0, 4), (0, 5), (0, 6), (1, 6),
                    (2, 6), (2, 5), (2, 4), (3, 4),
                    (4, 4), (4, 5), (4, 6)  # 2
                ]
        patern_height = 5
        pattern_width = 7

        maze_height = len(grid)
        maze_width = len(grid[0])
        if maze_height > patern_height or maze_width > pattern_width:
            start_row = (maze_height - patern_height) // 2
            start_col = (maze_width - pattern_width) // 2
            for p_r, p_c in pattern_42:
                maze_row = p_r + start_row
                maze_col = p_c + start_col
                if (
                    (self.entry[0] == maze_row and self.entry[1] == maze_col)
                    or
                    (self.exit[0] == maze_row and self.exit[1] == maze_col)
                ):
                    print("[!] Entry and Exit must not be in 42 pattern")
                    exit(0)
                grid[maze_row][maze_col].visited = True
                grid[maze_row][maze_col].is_42 = True
            return grid
        else:
            print("[!] Height and width is too small for 42 pattern  so ommiting\n")
            return grid

    def dfs(self, cell: Cell):

        current_cell = self.grid[cell.row][cell.col]
        current_cell.visited = True

        directions = list(Direction)
        shuffle(directions)

        for direction in directions:
            new_row = current_cell.row + direction.step[0]
            new_col = current_cell.col + direction.step[1]

            if not 0 <= new_row < self.height or not 0 <= new_col < self.width:
                continue

            neighbor = self.grid[new_row][new_col]

            if not neighbor.visited:
                current_cell.walls = current_cell.walls & ~direction
                neighbor.walls = neighbor.walls & ~direction.opposite

                self.dfs(neighbor)

    def print_maze(self):
        print("+" + "----+" * self.width)

        for row in self.grid:
            line = "|"

            for cell in row:
                if cell.is_42:
                    value = "\033[31m 42 \033[0m"  # Red 42
                else:
                    value = "    "

                if cell.walls & Direction.EAST:
                    line += value + "|"
                else:
                    line += value + " "

            print(line)

            line = "+"

            for cell in row:
                if cell.walls & Direction.SOUTH:
                    line += "----+"
                else:
                    line += "    +"

            print(line)
