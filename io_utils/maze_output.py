from __future__ import annotations

from random import choice

from mazegen.cell import Direction


class MazeOutput:
    """Display the maze and write the file output."""

    COLORS = [
        "\033[37m",  # white
        "\033[31m",  # red
        "\033[32m",  # green
        "\033[33m",  # yellow
        "\033[34m",  # blue
        "\033[35m",  # magenta
        "\033[36m",  # cyan
    ]

    RESET = "\033[0m"

    def __init__(self, grid, entry, exit, output_file):
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.output_file = output_file

        self.wall_color = self.COLORS[0]
        self.pattern_color = self.COLORS[1]

    def save_maze(self, path):
        output = ""

        # Maze walls
        for row in self.grid:
            for cell in row:
                output += f"{cell.walls:X}"
            output += "\n"

        # Entry and exit
        output += "\n"
        output += f"{self.entry[0]},{self.entry[1]}\n"
        output += f"{self.exit[0]},{self.exit[1]}\n"

        # Shortest path
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
        # Top border
        print(
            self.wall_color
            + "+"
            + "-----+" * len(self.grid[0])
            + self.RESET
        )

        for row in self.grid:
            line = self.wall_color + "|"

            for cell in row:

                # Entry
                if cell.row == self.entry[0] and cell.col == self.entry[1]:
                    value = " S   "

                # Exit
                elif cell.row == self.exit[0] and cell.col == self.exit[1]:
                    value = " E   "

                # Shortest path
                elif path and cell in path:
                    value = "\033[32m **  \033[0m"

                # 42 pattern
                elif cell.is_42:
                    value = (
                        self.pattern_color
                        + " 42  "
                        + self.RESET
                    )

                # Empty cell
                else:
                    value = "     "

                # East wall
                if cell.walls & Direction.EAST:
                    line += value + self.wall_color + "|"
                else:
                    line += value + " "

            print(line + self.RESET)

            # South walls
            line = self.wall_color + "+"

            for cell in row:
                if cell.walls & Direction.SOUTH:
                    line += "-----+"
                else:
                    line += "     +"

            print(line + self.RESET)

    def change_color(self):
        """Choose a random wall color."""
        self.wall_color = choice(self.COLORS)

    def change_42_color(self):
        """Choose a random 42 color."""
        self.pattern_color = choice(self.COLORS)

    def run(self, generator):
        """Run the interactive maze display."""

        show_path = False

        while True:
            # Keep the output object connected to the current grid
            self.grid = generator.grid

            # Calculate path only when it should be displayed
            if show_path:
                path = generator.bfs()
            else:
                path = None

            # Display maze
            self.print_maze(path)

            print()
            print("[R] Regenerate")
            print("[S] Show/Hide solution")
            print("[C] Change wall color")
            print("[4] Change 42 color")
            print("[Q] Quit")

            command = input("> ").lower()

            # Regenerate
            if command == "r":
                generator.grid = generator.grid_init()
                generator.generate_maze()

            # Show / hide shortest path
            elif command == "s":
                show_path = not show_path

            # Change wall color
            elif command == "c":
                self.change_color()

            # Change 42 color
            elif command == "4":
                self.change_42_color()

            # Quit
            elif command == "q":
                break
