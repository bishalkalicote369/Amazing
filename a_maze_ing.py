from __future__ import annotations

import sys
from parsing import get_conf


def main() -> None:
    print()
    get_conf(sys.argv[1])


if __name__ == "__main__":
    main()
