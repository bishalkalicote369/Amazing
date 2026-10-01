from __future__ import annotations

from typing import Final
from random import randint
from io_utils import ConfigModel, load_config
from .cell import (
    Cell,
    STEP,
    WALLS,
    OPPOSITE,
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

        self.grid = self.grid_init()

    def grid_init(self):
        grid = []
        for row in range(self.height):
            current_row = []
            for col in range(self.width):
                current_row.append(Cell(row, col))
            grid.append(current_row)
        return grid

    # def add_pattern(self):
    #     pattern = [
    #         "#   ###",
    #         "#     #",
    #         "### ###",
    #         "  # #  ",
    #         "  # ###"
    #     ]


    # def show_maze(self):
    #     for row in self.grid:
    #         for cell in row:
    #             # print(f"({cell.row},{cell.col})", end=" ")
    #             # print(cell.walls - dir)
    #         print(end="\n\n")
