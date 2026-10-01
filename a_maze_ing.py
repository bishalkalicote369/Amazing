from __future__ import annotations

from sys import exit, argv
from io_utils import load_config, ConfigModel
from src import MazeGenerator


EXIT_OK = 0
EXIT_MALFORMED = 1
MISSING_ARGUMENT = """Error: missing required argument

Usage:
    python3 a_maze_ing.py <file_name.txt>

Example:
    python3 a_maze_ing.py maze.txt"""


def main() -> int:
    """Generate the maze from the configuration file.

    Reads the configuration file provided as a command-line argument,
    generates the maze, displays it, and writes the result to the
    output file.

    Returns:
        int: EXIT_OK on success, or EXIT_MALFORMED if the argument is invalid.
    """
    if len(argv) != 2:
        print(MISSING_ARGUMENT)
        return EXIT_MALFORMED

    try:
        amazeing = MazeGenerator(argv[1])
        amazeing.grid_init()
        amazeing.show_maze()
    except FileNotFoundError as ERROR:
        print(ERROR)
    except PermissionError as ERROR:
        print(ERROR)
    except ValueError as ERROR:
        print(ERROR)
    except Exception as ERROR:
        print(ERROR)
    return EXIT_OK


if __name__ == "__main__":
    exit(main())
