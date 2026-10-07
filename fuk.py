class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


def get_maze(height: int, width: int):
    maze = []
    for x in range(height):
        row = []
        for y in range(width):
            row.append(Cell(x, y))
        maze.append(row)
    return maze


def main() -> None:
    print(" " * 20 + "========== MAZE =========")
    print()
    pattern_42 = [
        (0, 0), (1, 0), (2, 0), (2, 1),
        (2, 2), (3, 2), (4, 2), (0, 4), (0, 5),
        (0, 6), (1, 6), (2, 6), (2, 5), (2, 4),
        (3, 4), (4, 4), (4, 5), (4, 6)

    ]

    height = 10
    width = 10
    maze = get_maze(height, width)
    for row in maze:
        for cell in row:
            if (cell.row, cell.col) in pattern_42:
                print("*", end=" ")
            else:
                print(" ", end=" ")
        print()

if __name__ == "__main__":
    main()
