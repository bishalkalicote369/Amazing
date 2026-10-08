from __future__ import annotations

from typing import Final
from random import (
    randint,
    seed,
    shuffle
)
from .cell import (
    Cell,
    Direction,
)


class MazeGenerator:
    """Generate maze based on validated configuration"""
    def __init__(self,
                 height: int,
                 width: int,
                 entry: tuple[int, int],
                 exit: tuple[int, int],
                 perfect: bool,
                 seeds: int | None) -> None:

        self.height: Final[int] = height
        self.width: Final[int] = width
        self.entry: Final[tuple[int, int]] = entry
        self.exit: Final[tuple[int, int]] = exit
        self.perfect: Final[bool] = perfect
        self.seed: Final[int | None] = (
            seeds
            if seeds is not None
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
                grid[maze_row][maze_col].is_42 = True
            return grid
        else:
            print(
                "Height and width is too small for 42 pattern so ommiting\n"
                )
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

            if not neighbor.visited and not neighbor.is_42:
                current_cell.walls = current_cell.walls & ~direction
                neighbor.walls = neighbor.walls & ~direction.opposite

                self.dfs(neighbor)

    def count_open_walls(self, cell):
        count = 0

        for direction in Direction:
            if not (cell.walls & direction):
                count += 1
        return count

    def add_loops(self):

        cells = []
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

                directions = list(Direction)
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

    def reset_visited(self):
        for row in self.grid:
            for cell in row:
                cell.visited = False

    def bfs(self):
        self.reset_visited()
        entry = self.grid[self.entry[0]][self.entry[1]]
        exit = self.grid[self.exit[0]][self.exit[1]]

        queue = [entry]
        entry.visited = True
        came_from = {}

        while queue:
            current = queue.pop(0)
            if current == exit:
                break
            for direction in Direction:
                new_row = current.row + direction.step[0]
                new_col = current.col + direction.step[1]

                if not 0 <= new_row < self.height:
                    continue
                if not 0 <= new_col < self.width:
                    continue
                neighbor = self.grid[new_row][new_col]
                if not (current.walls & direction) and not neighbor.visited:
                    came_from[neighbor] = current
                    neighbor.visited = True
                    queue.append(neighbor)

        path = []
        current = exit

        while current != entry:
            path.append(current)
            current = came_from[current]
        path.append(entry)

        path.reverse()
        return path

    def generate_maze(self):
        start_cell = self.grid[self.entry[0]][self.entry[1]]

        if self.perfect:
            self.dfs(start_cell)
        else:
            self.dfs(start_cell)
            self.add_loops()
