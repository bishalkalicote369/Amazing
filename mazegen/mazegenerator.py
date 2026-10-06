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
