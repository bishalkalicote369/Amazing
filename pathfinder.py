from __future__ import annotations
from mazegen.cell import Cell, Direction
from mazegen import MazeError


class PathFinder:
    "Find the shortest path from the generated maze"
    def __init__(
            self,
            height: int,
            width: int,
            entry: tuple[int, int],
            exit: tuple[int, int],
            grid: list[list[Cell]]
    ) -> None:
        self.height: int = height
        self.width: int = width
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.grid: list[list[Cell]] = grid

    def reset_visited(self) -> None:
        """
        Reset the visited state of every cell.

        Returns:
            None.
        """
        for row in self.grid:
            for cell in row:
                cell.visited = False

    def bfs(self) -> list[Cell]:
        """
        Find the shortest path from entry to exit using BFS.

        Reset the visited state, explore reachable cells, and
        reconstruct the path from the exit back to the entry.

        Returns:
            A list of cells representing the path from entry to exit.

        Raises:
            MazeError: If the exit cannot be reached.
        """
        self.reset_visited()

        entry_cell = self.grid[self.entry[0]][self.entry[1]]
        exit_cell = self.grid[self.exit[0]][self.exit[1]]

        queue: list[Cell] = [entry_cell]
        entry_cell.visited = True

        came_from: dict[Cell, Cell] = {}

        while queue:
            current = queue.pop(0)

            if current == exit_cell:
                break

            for direction in Direction:
                new_row = current.row + direction.step[0]
                new_col = current.col + direction.step[1]

                if not 0 <= new_row < self.height:
                    continue

                if not 0 <= new_col < self.width:
                    continue

                neighbor = self.grid[new_row][new_col]

                if (
                    not (current.walls & direction)
                    and not neighbor.visited
                ):
                    came_from[neighbor] = current
                    neighbor.visited = True
                    queue.append(neighbor)

        if not exit_cell.visited:
            raise MazeError("No path exists from entry to exit.")

        path: list[Cell] = []
        current = exit_cell

        while current != entry_cell:
            path.append(current)
            current = came_from[current]

        path.append(entry_cell)
        path.reverse()

        return path
