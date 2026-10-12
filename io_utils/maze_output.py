from __future__ import annotations

from random import choice

from mazegen.cell import Direction, Cell
from mazegen.mazegenerator import MazeGenerator
from pathfinder import PathFinder


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

    BG_COLORS = [
        "\033[40m",  # black
        "\033[41m",  # red
        "\033[42m",  # green
        "\033[43m",  # yellow
        "\033[44m",  # blue
        "\033[45m",  # magenta
        "\033[46m",  # cyan
        "\033[47m",  # white
    ]

    RESET = "\033[0m"
    BLACK = "\033[30m"
    WHITE = "\033[37m"

    def __init__(self,
                 grid: list[list[Cell]],
                 entry: tuple[int, int],
                 exit: tuple[int, int],
                 output_file: str) -> None:
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.output_file = output_file

        # Wall and 42 text colors
        self.wall_color = self.COLORS[0]
        self.pattern_color = self.COLORS[1]

        # Background colors
        self.start_bg = "\033[42m"    # Green background
        self.exit_bg = "\033[41m"     # Red background
        self.pattern_bg = "\033[44m"  # Blue background

    def save_maze(self, path: list[Cell]) -> None:
        """Save maze walls, entry, exit, and shortest path."""

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

        # Shortest path directions
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

    def print_maze(self, path: list[Cell]) -> None:
        """Print the maze with colored walls and backgrounds."""

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

                # Entry: S with green background
                if (
                    cell.row == self.entry[0]
                    and cell.col == self.entry[1]
                ):
                    value = (
                        self.start_bg
                        + self.BLACK
                        + "  S  "
                        + self.RESET
                    )

                # Exit: E with red background
                elif (
                    cell.row == self.exit[0]
                    and cell.col == self.exit[1]
                ):
                    value = (
                        self.exit_bg
                        + self.WHITE
                        + "  E  "
                        + self.RESET
                    )

                # Shortest path: yellow background
                elif path and cell in path:
                    value = (
                        self.WHITE
                        + " **  "
                        + self.RESET
                    )

                # 42 pattern: changeable background
                elif cell.is_42:
                    value = (
                        self.pattern_bg
                        + self.pattern_color
                        + "     "
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

    def change_color(self) -> None:
        """Choose a random wall color."""
        self.wall_color = choice(self.COLORS)

    def change_42_background(self) -> None:
        """Choose a random background color for the 42 pattern."""
        self.pattern_bg = choice(self.BG_COLORS)

    def run(self, path_finder: PathFinder, generator: MazeGenerator) -> None:
        """Run the interactive maze display."""

        show_path = False

        while True:
            # Keep output connected to the current grid
            self.grid = generator.grid

            # Calculate path only when displayed
            if show_path:
                path = path_finder.bfs()
            else:
                path = None

            # Display maze
            self.print_maze(path if path is not None else [])

            print()
            print("[R] Regenerate")
            print("[S] Show/Hide solution")
            print("[C] Change wall color")
            print("[B] Change 42 pattern color")
            print("[Q] Quit")

            command = input("> ").lower()

            # Regenerate maze
            if command == "r":
                generator.grid = generator.grid_init()
                generator.generate_maze()
                path_finder.grid = generator.grid

            # Show / hide shortest path
            elif command == "s":
                show_path = not show_path

            # Change wall color
            elif command == "c":
                self.change_color()

            # Change only the 42 background
            elif command == "b":
                self.change_42_background()

            # Quit
            elif command == "q":
                break
