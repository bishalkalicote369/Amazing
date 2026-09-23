from __future__ import annotations

import sys
from messages import MISSING_ARGUMENT
from io_utils import load_config, ConfigModel


EXIT_OK = 0
EXIT_MALFORMED = 1


def main() -> int:
    """Generate the maze from the configuration file.

    Reads the configuration file provided as a command-line argument,
    generates the maze, displays it, and writes the result to the
    output file.

    Returns:
        int: EXIT_OK on success, or EXIT_MALFORMED if the argument is invalid.
    """
    if len(sys.argv) != 2:
        print(MISSING_ARGUMENT)
        return EXIT_MALFORMED
    try:
        config: ConfigModel = load_config(sys.argv[1])
        print(config.HEIGHT)
        print(config.WIDTH)
        print(config.ENTRY)
        print(config.EXIT)
        print(config.OUTPUT_FILE)
        print(config.PERFECT)
        print(config.SEED)
    except FileNotFoundError as ERROR:
        print(ERROR)
    except PermissionError as ERROR:
        print(ERROR)
    except ValueError as ERROR:
        print(ERROR)

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
