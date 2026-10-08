from __future__ import annotations

from mazegen.cell import (
    Direction,
)


class MazeOutput:
    "Display the maze and write the file output"
    def __init__(self, grid, entry, exit, output_file):
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.output_file = output_file

    def save_maze(self, path):
        output = ""
        for row in self.grid:
            for cell in row:
                output += f"{cell.walls:X}"
            output += "\n"

        output += "\n"
        output += f"{self.entry[0]},{self.entry[1]}\n"
        output += f"{self.exit[0]},{self.exit[1]}\n"
        directions = ""

        for i in range(len(path) - 1):
            current = path[i]
            next_cell = path[i + 1]

            if next_cell.row < current.row:
                directions += "N"
            elif next_cell.col > current.col:
                directions += "E"
            elif next_cell.row > current.row:
                directions += "S"
            elif next_cell.col < current.col:
                directions += "W"

        output += directions + "\n"

        with open(self.output_file, "w") as file:
            file.write(output)

    def print_maze(self, path=None):
        print("+" + "----+" * len(self.grid[0]))

        for row in self.grid:
            line = "|"

            for cell in row:
                if cell.row == self.entry[0] and cell.col == self.entry[1]:
                    value = " S  "
                elif cell.row == self.exit[0] and cell.col == self.exit[1]:
                    value = " E  "
                elif path and cell in path:
                    value = "\033[32m ** \033[0m"
                elif cell.is_42:
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
