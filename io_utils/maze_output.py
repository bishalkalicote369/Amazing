from __future__ import annotations

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
        print(
            self.wall_color
            + "+"
            + "----+" * len(self.grid[0])
            + self.RESET
        )

        for row in self.grid:
            line = self.wall_color + "|"

            for cell in row:

                if cell.row == self.entry[0] and cell.col == self.entry[1]:
                    value = " S  "

                elif cell.row == self.exit[0] and cell.col == self.exit[1]:
                    value = " E  "

                elif path and cell in path:
                    value = "\033[32m ** \033[0m"

                elif cell.is_42:
                    value = "\033[31m 42 \033[0m"

                else:
                    value = "    "

                if cell.walls & Direction.EAST:
                    line += value + self.wall_color + "|"
                else:
                    line += value + " "

            print(line + self.RESET)

            line = self.wall_color + "+"

            for cell in row:
                if cell.walls & Direction.SOUTH:
                    line += "----+"
                else:
                    line += "    +"

            print(line + self.RESET)

    def change_color(self):
        print("\nChoose wall color:")
        print("1. White")
        print("2. Red")
        print("3. Green")
        print("4. Yellow")
        print("5. Blue")
        print("6. Magenta")
        print("7. Cyan")

        choice = input("> ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(self.COLORS):
                self.wall_color = self.COLORS[choice - 1]

    def run(self, generator):
        show_path = False

        while True:
            self.grid = generator.grid

            if show_path:
                path = generator.bfs()
            else:
                path = None

            self.print_maze(path)

            print()
            print("[R] Regenerate")
            print("[S] Show/Hide solution")
            print("[C] Change wall color")
            print("[Q] Quit")

            choice = input("> ").lower()

            if choice == "r":
                generator.grid = generator.grid_init()
                generator.generate_maze()

            elif choice == "s":
                show_path = not show_path

            elif choice == "c":
                self.change_color()

            elif choice == "q":
                break
