from __future__ import annotations

from sys import exit, argv
from mazegen import MazeGenerator
from io_utils import MazeOutput
from io_utils import (
    ConfigModel,
    load_config
)


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
        config: ConfigModel = load_config(argv[1])
        amazeing = MazeGenerator(
            config.HEIGHT,
            config.WIDTH,
            config.ENTRY,
            config.EXIT,
            config.PERFECT,
            config.SEED
            )
        amazeing.generate_maze()

        path = amazeing.bfs()

        output = MazeOutput(
            amazeing.grid,
            amazeing.entry,
            amazeing.exit,
            config.OUTPUT_FILE
        )
        output.save_maze(path)
        output.print_maze(path)
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
