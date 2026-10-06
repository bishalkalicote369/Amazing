# Mazes in Python (OOP): The Complete Beginner Guide

*Based on "Mazes for Programmers" by Jamis Buck, rewritten from Ruby to modern Python (3.10+) with classes, type hints, and a direct mapping to the 42 project **A-Maze-ing**.*

---

## How to use this guide

| If you want to... | Read |
|---|---|
| Understand what a maze *is* (math and vocabulary) | Part 1 |
| Refresh the Python OOP you need | Part 2 |
| Build the core classes (`Cell`, `Grid`) | Part 3 |
| Learn all 12 algorithms with code | Part 4 |
| Solve mazes, measure them, color them | Part 5 |
| Print a maze in the terminal | Part 6 |
| Force shapes (like the "42") and loops | Parts 7 and 8 |
| See polar, hex, triangle, weave, 3D, cube, sphere mazes | Part 9 |
| Build the A-Maze-ing project step by step | Part 10 |
| Compare algorithms, review, practice | Part 11 |

**Conventions**

- Every Python block is real code. Blocks are in order: later blocks use classes defined by earlier ones.
- When you split code into files (`mazegen/cell.py`, `mazegen/grid.py`, ...), add the imports between your own files (for example `from .cell import Cell`).
- A block that starts with `# snippet` is only an illustration (not meant to run alone).
- Code follows the A-Maze-ing rules: type hints everywhere, docstrings, `flake8` style (79 columns).
- Coordinates: **`row` goes down, `column` goes right**, row 0 is the top. "North" means `row - 1`.

---

# Part 1: The Theory

## 1.1 What is a maze?

A maze built on a grid is made of only four ideas:

| Word | Meaning |
|---|---|
| **Grid** | A table of rows and columns |
| **Cell** | One square of the table (one "room") |
| **Wall** | The border between two neighbouring cells (or between a cell and the outside) |
| **Passage** (or *link*) | A wall that has been removed, so you can walk between two cells |

You start from a grid where **every wall is closed** and you **remove some walls** (this is called *carving*). The result is a maze. The only question is: *which walls do we remove, and in what order?* Each maze algorithm answers this differently.

A tiny 3×3 perfect maze (the lines are walls, spaces are passages):

```text
+---+---+---+
|           |
+---+---+   +
|           |
+   +---+---+
|           |
+---+---+---+
```

Walk from the top-left cell: right, right, down, left, left, down, right, right. There is only one way. That is a **perfect maze**.

### Entrance and exit

A perfect maze has a path between *any* two cells. So you can pick any two cells as start and finish (for example two border cells) and a solution is guaranteed. The generation algorithm does not care about the entrance or exit. You choose them afterwards.

## 1.2 Kinds of mazes

| Kind | Definition |
|---|---|
| **Perfect maze** | Every cell reaches every other cell by **exactly one** path. No loops. "Perfect" is mathematical, not a quality judgement. |
| **Braid maze** | No dead ends, with many loops. The opposite of perfect. |
| **Partially braided** | Some dead ends removed, some kept. |
| **Sparse maze** | Does not fill the whole grid (some cells removed). |
| **Weave maze** | Passages cross over and under each other like spaghetti. |
| **Unicursal** | A single path with no branches (a "labyrinth" for some people). |
| **Multicursal** | Has branches. Everything in this guide is multicursal. |

## 1.3 Graph theory (the hidden math behind mazes)

You do **not** need proofs, but these words make everything easier.

- **Node (vertex)**: here, a cell.
- **Edge**: here, a possible or carved passage between two neighbouring cells.
- **Path**: a sequence of connected cells.
- **Loop (cycle)**: a path that comes back to where it started.
- **Connected graph**: every node can be reached from every other node.
- **Tree**: a connected graph with **no loops**.
- **Spanning tree**: a tree that touches **all** the nodes of a bigger graph.

The key sentence:

> **A perfect maze is a spanning tree of the grid graph.**

Think of the grid as a graph where every cell is linked to its 4 neighbours (all walls open). Choosing a spanning tree means keeping the minimum number of passages so that everything is still reachable and there is no loop.

Useful consequences:

1. **A perfect maze with `n` cells has exactly `n − 1` passages.** Fewer means some cell is unreachable. More means a loop.
2. Connected + no loops ⇒ exactly one path between any two cells.
3. Adding one extra passage to a perfect maze creates exactly one loop. This is how **braiding** works (Part 8).
4. A **minimum spanning tree** is the spanning tree with the lowest total edge cost. Kruskal's and Prim's algorithms were invented for it, and they became maze algorithms.

### Cell types by number of passages (the "degree")

| Passages | Name |
|---|---|
| 1 | **Dead end** |
| 2 | Corridor (straight) or elbow (turn) |
| 3 | T-junction (three-way) |
| 4 | Crossroad (four-way) |

## 1.4 What is an algorithm?

An algorithm is a **recipe**: a list of steps that always reaches the goal. A *maze algorithm* is a recipe for choosing which walls to remove. In this book almost all of them use **randomness**: every choice ("north or east?") is made by chance, so each maze is different.

### How we compare algorithms

- **Speed** (time): usually written with Big-O. `O(n)` means "the work grows in proportion to the number of cells `n`". It is the best possible when every cell must be visited.
- **Memory**: how much extra data the algorithm needs (a stack? a set per cell?).
- **Simplicity**: how easy it is to code and to explain.
- **Bias** and **texture**: see below.
- **Flexibility**: does it work on masks, hexagons, 3D?

## 1.5 Randomness, bias and texture

### Texture

The **texture** of a maze is its visual style: long or short corridors, preferred directions, many or few dead ends.

### Bias

A **bias** belongs to the *algorithm*. It means the algorithm does not choose fairly among all possible mazes, so a certain texture appears in almost every maze it makes.

The "bag of mazes" picture: imagine every possible perfect maze for your grid in a big bag. A perfect random generator picks one at random with the same chance for each.

For a 2×2 grid there are exactly **4** perfect mazes. How many can each algorithm create?

| Algorithm | Reachable mazes (of 4) |
|---|---|
| Binary Tree | 2 (50%): it always makes unbroken north and east corridors |
| Sidewinder | 3 (75%): it always makes an unbroken north corridor |
| Aldous-Broder, Wilson's | 4 (100%), each equally likely |

An algorithm can be *uniform* (every maze equally likely) or *non-uniform* (some mazes more likely). Bias can also be invisible to the eye. Only statistics reveal it.

**Biases are not always bad.** A bias gives personality: the long winding "river" of the Recursive Backtracker is a bias that many people like. Choose the bias that fits your project.

### Seeds: random but reproducible

Computers do not have true randomness. They use a **pseudo-random number generator (PRNG)**: a formula that produces numbers that *look* random, starting from a **seed**. Same seed ⇒ same sequence ⇒ same maze. Python gives you `random.Random(seed)`. This is required by A-Maze-ing ("the same seed must always produce the same maze").

Rule for reproducibility: **create one `random.Random(seed)` object and use it for every random choice**. Never mix in the global `random` module or iterate over a `set` of objects (set order can change between runs).

## 1.6 The family of algorithms

| Family | Idea | Algorithms |
|---|---|---|
| **Simple local choice** | Look at each cell once and choose a direction | Binary Tree, Sidewinder |
| **Random walks** | Walk around randomly | Aldous-Broder, Wilson's |
| **Constrained walks (carvers)** | Walk but never step on visited cells; recover from dead ends | Hunt-and-Kill, Recursive Backtracker |
| **Set merging (spanning trees)** | Give every cell a set id and merge sets by removing walls | Kruskal's, Eller's |
| **Growing from a frontier** | Keep a list of active cells and grow outward | Prim's (two versions), Growing Tree |
| **Wall adders** | Start open and add walls | Recursive Division |

Two words to remember:

- **Passage carver**: starts with all walls and removes some (almost all algorithms).
- **Wall adder**: starts with no walls and adds some (Recursive Division).

## 1.7 Data structures you will meet

| Structure | Rule | Python tool | Used by |
|---|---|---|---|
| **List** | Ordered items, random access | `list` | everywhere |
| **Stack** | Last in, first out (LIFO) | `list` with `append` / `pop` | Recursive Backtracker |
| **Queue** | First in, first out (FIFO) | `collections.deque` | Breadth-first search / Dijkstra (equal costs) |
| **Dictionary** | Key → value lookup | `dict` | Distances, sets of cells |
| **Set of ids** | "Which group is this cell in?" | `dict[Cell, int]` | Kruskal's, Eller's |
| **Priority queue** | Always give me the cheapest item | `heapq` | Weighted Dijkstra, efficient True Prim's |
| **Bitmask** | Several yes/no values in one integer | `int` with `\|`, `&` | The hex output of A-Maze-ing |

## 1.8 Dimensions

A "dimension" is the number of coordinates needed to name a cell.

| Dimensions | Coordinates | Example |
|---|---|---|
| 0 | none | a single cell |
| 1 | position | a corridor |
| 2 | row, column | a normal maze |
| 3 | level, row, column | a building with floors |
| 4 | + a fourth axis ("hither/yon") | stacks of buildings |

Mazes painted on the surface of a 3D object (cylinder, cube, sphere) are still **2D**: you walk on the surface. They are called *planair* mazes.

## 1.9 Costs and weights

Sometimes a step is not "one unit". A lava cell costs 50, a normal cell costs 1. A cost on a cell or a passage is called a **weight**. *Distance* is just the special case where every weight is 1. Dijkstra's algorithm finds the **cheapest** path, which is not always the **shortest** one (Part 5).

## 1.10 Two coordinate systems (a classic trap)

- Inside the grid we usually write **`(row, column)`**: `grid[row, column]`.
- A-Maze-ing and drawing code write **`(x, y)`**: `x` is the column, `y` is the row.

`(x, y) = (column, row)`. Converting is easy to forget. Always name your variables (`row`, `column`, `x`, `y`) and convert in exactly one place.

## 1.11 Bits and hexadecimal (needed for the output file)

Four yes/no values (the four walls of a cell) fit in **4 bits**. A hexadecimal digit (`0`..`9`, `A`..`F`) represents exactly 4 bits:

| Hex | Binary | Hex | Binary |
|---|---|---|---|
| 0 | 0000 | 8 | 1000 |
| 1 | 0001 | 9 | 1001 |
| 2 | 0010 | A | 1010 |
| 3 | 0011 | B | 1011 |
| 4 | 0100 | C | 1100 |
| 5 | 0101 | D | 1101 |
| 6 | 0110 | E | 1110 |
| 7 | 0111 | F | 1111 |

Python: `value |= 4` sets bit 2, `value & 4` tests it, `format(value, "X")` gives the hex digit.

---

# Part 2: Python OOP Primer (with maze examples)

Object-oriented programming (OOP) means: model the problem with **objects** that carry data and behaviour. A maze maps perfectly onto it: a `Grid` *has* many `Cell`s, an algorithm *is a* `MazeAlgorithm`.

```python
# snippet
class Point:
    """A class is a blueprint."""

    def __init__(self, x: int, y: int) -> None:   # constructor
        self.x = x                                # attributes (data)
        self.y = y

    def move_right(self) -> None:                 # method (behaviour)
        self.x += 1


p = Point(2, 3)      # an object (an instance of the class)
p.move_right()
print(p.x)           # 3
```

| OOP idea | Meaning | Where it appears in the maze code |
|---|---|---|
| **Class / object** | Blueprint / one thing built from it | `Cell`, `Grid`, one `Grid(10, 10)` |
| **Attribute** | Data stored in an object | `cell.row`, `cell.north` |
| **Method** | Function that belongs to a class | `cell.link(other)` |
| **Encapsulation** | Hide internals behind methods. A leading `_` means "private by convention". | `cell._links` is changed only by `link` / `unlink` |
| **Inheritance** | A class reuses another and adds to it: `class HexCell(Cell)` | `HexCell`, `PolarGrid`, `Grid3D` |
| **`super()`** | Call the parent version of a method | `super().__init__(row, column)` |
| **Polymorphism** | Same method name, different behaviour per class | Every cell type has `neighbors()`. Algorithms do not care which kind. |
| **Abstraction (ABC)** | A class that only defines *what* subclasses must do | `MazeAlgorithm.generate()` |
| **Composition** | An object is made of other objects ("has a") | `Grid` has `Cell`s. `MazeGenerator` has a `Grid` and an algorithm. |
| **Strategy pattern** | Swap behaviour by swapping an object | `MazeGenerator(algorithm=Wilsons())` |
| **Template method / hook** | Parent calls a method that children may override | `Grid.__str__` calls `contents_of(cell)` |
| **Dunder methods** | Special names Python calls for you | `__str__` (for `print`), `__getitem__` (for `grid[r, c]`), `__contains__` (for `in`) |
| **Generators** | `yield` produces items one by one | `Grid.each_cell()` |
| **Dataclass** | Class that mainly holds data, with less typing | `MazeConfig` |
| **Type hints** | Annotations checked by `mypy` | `def link(self, other: Cell) -> Cell:` |

```python
# snippet
from abc import ABC, abstractmethod


class Animal(ABC):                    # abstract: cannot be built directly
    @abstractmethod
    def speak(self) -> str: ...       # children MUST implement this


class Dog(Animal):                    # inheritance
    def speak(self) -> str:
        return "woof"
```

That is the exact structure we use for algorithms: `MazeAlgorithm` (abstract) and `BinaryTree`, `Wilsons`, `Kruskals`, ... (concrete).

---

# Part 3: The Core Classes

## 3.1 Design

```text
Grid  ──has many──►  Cell  ──linked to──►  other Cells (passages)
  │                    │
  │                    └─ knows its 4 neighbours: north, south, east, west
  └─ owns the random generator (seed) and the cells

MazeAlgorithm (abstract)
  ├── BinaryTree, Sidewinder, AldousBroder, Wilsons, HuntAndKill,
  ├── RecursiveBacktracker, Kruskals, SimplifiedPrims, TruePrims,
  └── GrowingTree, Ellers, RecursiveDivision
```

Important idea: a cell has **neighbours** (cells next to it in the grid) and **links** (neighbours it is connected to by a removed wall). Neighbours never change. Links are the maze.

## 3.2 The `Cell` class

```python
# mazegen/cell.py  (imports for the whole guide, shown once)
from __future__ import annotations

import heapq
import itertools
import math
import random
import sys
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Optional


class Cell:
    """One square of the maze.

    A cell knows where it is (row, column), who its neighbours are in the
    four directions, and which neighbours it is linked to by a passage.
    """

    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.column = column
        self.north: Optional[Cell] = None
        self.south: Optional[Cell] = None
        self.east: Optional[Cell] = None
        self.west: Optional[Cell] = None
        self.blocked = False
        # A dict (not a set) keeps insertion order, so seeded mazes are
        # reproducible from one run to the next.
        self._links: dict[Cell, bool] = {}

    def link(self, other: Cell, bidirectional: bool = True) -> Cell:
        """Remove the wall between this cell and *other*."""
        self._links[other] = True
        if bidirectional:
            other.link(self, False)
        return self

    def unlink(self, other: Cell, bidirectional: bool = True) -> Cell:
        """Put the wall back between this cell and *other*."""
        self._links.pop(other, None)
        if bidirectional:
            other.unlink(self, False)
        return self

    def links(self) -> list[Cell]:
        """Cells connected to this one by a passage."""
        return list(self._links)

    def is_linked(self, other: Optional[Cell]) -> bool:
        """True if there is a passage to *other* (False for None)."""
        return other is not None and other in self._links

    def neighbors(self) -> list[Cell]:
        """Adjacent cells that exist (linked or not)."""
        around = (self.north, self.south, self.east, self.west)
        return [cell for cell in around if cell is not None]

    def detach(self) -> None:
        """Cut this cell off from the grid and mark it blocked."""
        for other in self.neighbors():
            if other.north is self:
                other.north = None
            if other.south is self:
                other.south = None
            if other.east is self:
                other.east = None
            if other.west is self:
                other.west = None
        self.north = self.south = self.east = self.west = None
        self.blocked = True
```

Why `bidirectional`? A passage between A and B must exist in **both** cells (this is the "wall coherence" rule of A-Maze-ing). `link` records it on both sides; the inner call passes `False` to stop the two cells from calling each other forever.

## 3.3 The `Grid` class

```python
# mazegen/grid.py
class Grid:
    """A rectangle of cells plus the random generator used to carve it."""

    def __init__(
        self,
        rows: int,
        columns: int,
        seed: Optional[int] = None,
        blocked: Iterable[tuple[int, int]] = (),
    ) -> None:
        if rows < 1 or columns < 1:
            raise ValueError("rows and columns must be at least 1")
        self.rows = rows
        self.columns = columns
        self.seed = seed
        self.rng = random.Random(seed)
        self.labels: dict[Cell, str] = {}
        self._grid = self._prepare_grid()
        self._configure_cells()
        for row, column in blocked:
            self.at(row, column).detach()

    def _prepare_grid(self) -> list[list[Cell]]:
        """Create the cells (subclasses override this)."""
        return [[Cell(r, c) for c in range(self.columns)]
                for r in range(self.rows)]

    def _configure_cells(self) -> None:
        """Tell every cell who its neighbours are."""
        for cell in self.each_cell():
            row, col = cell.row, cell.column
            cell.north = self[row - 1, col]
            cell.south = self[row + 1, col]
            cell.west = self[row, col - 1]
            cell.east = self[row, col + 1]

    def __getitem__(self, position: tuple[int, int]) -> Optional[Cell]:
        """grid[row, column] gives the cell, or None if out of bounds."""
        row, column = position
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return self._grid[row][column]
        return None

    def at(self, row: int, column: int) -> Cell:
        """Like grid[row, column] but raises IndexError if out of bounds."""
        cell = self[row, column]
        if cell is None:
            raise IndexError(f"no cell at row={row}, column={column}")
        return cell

    def each_row(self) -> Iterator[list[Cell]]:
        """Yield every row (including blocked cells)."""
        yield from self._grid

    def each_cell(self) -> Iterator[Cell]:
        """Yield every usable cell (blocked cells are skipped)."""
        for row in self._grid:
            for cell in row:
                if not cell.blocked:
                    yield cell

    def size(self) -> int:
        """Number of usable cells."""
        return sum(1 for _ in self.each_cell())

    def random_cell(self) -> Cell:
        """A usable cell chosen with the grid's own random generator."""
        return self.rng.choice(list(self.each_cell()))

    def deadends(self) -> list[Cell]:
        """Cells linked to exactly one other cell."""
        return [c for c in self.each_cell() if len(c.links()) == 1]

    # -- text display ----------------------------------------------------
    def contents_of(self, cell: Cell) -> str:
        """One character drawn inside a cell (hook for subclasses)."""
        return self.labels.get(cell, " ")

    def __str__(self) -> str:
        output = "+" + "---+" * self.columns + "\n"
        for row in self.each_row():
            top = "|"
            bottom = "+"
            for cell in row:
                if cell.blocked:
                    body = "###"
                else:
                    body = f" {self.contents_of(cell)} "
                east = " " if cell.is_linked(cell.east) else "|"
                top += body + east
                south = "   " if cell.is_linked(cell.south) else "---"
                bottom += south + "+"
            output += top + "\n" + bottom + "\n"
        return output
```

Things to notice:

- `__getitem__` lets you write `grid[2, 3]`. Python passes `(2, 3)` as a tuple. Returning `None` out of bounds makes border cells naturally have `north = None` and so on.
- `_prepare_grid` and `_configure_cells` are separate methods **on purpose**: subclasses (hex, polar, 3D) override them and everything else keeps working. This is the *template method* idea.
- `rng` lives in the grid so that all algorithms share one seeded generator.

A first test:

```python
grid = Grid(3, 3)
a, b = grid.at(0, 0), grid.at(0, 1)
a.link(b)
print(a.is_linked(b), b.is_linked(a))   # True True
print(grid)
```

---

# Part 4: The Twelve Algorithms

All algorithms share this base class (abstraction + strategy pattern):

```python
# mazegen/algorithms.py
class MazeAlgorithm(ABC):
    """Every maze algorithm *is a* MazeAlgorithm."""

    # Algorithms that rely on a perfect rectangle (no blocked cells)
    # set this to False.
    supports_mask = True

    @abstractmethod
    def generate(self, grid: Grid) -> Grid:
        """Carve passages into *grid* and return it."""
```

To use any of them: `SomeAlgorithm().generate(grid)`.

---

## 4.1 Binary Tree

**Idea.** For every cell, flip a coin: carve **north** or **east**. If one of these directions is outside the grid, take the other. The top-right cell has neither, so it is skipped.

**Why "tree"?** The result really is a binary tree: each cell has at most two "children". The top-right cell is the root.

**Texture / bias.**

- An unbroken corridor along the whole **north** row and the whole **east** column.
- A strong diagonal: walking from south-west to north-east is trivial (you can always go north or east), walking the other way is harder.
- Only 2 of the 4 possible 2×2 mazes can appear.

**Cost.** `O(n)` time, almost no memory. The simplest algorithm there is.

**Works on masks?** No. A blocked cell can leave a cell with no north or east exit.

```python
class BinaryTree(MazeAlgorithm):
    """For each cell, carve north or east."""

    supports_mask = False

    def generate(self, grid: Grid) -> Grid:
        for cell in grid.each_cell():
            options = [n for n in (cell.north, cell.east) if n is not None]
            if options:
                cell.link(grid.rng.choice(options))
        return grid
```

```python
maze = Grid(4, 4, seed=1)
BinaryTree().generate(maze)
print(maze)
```

**Variations.** Choose south/west (or any perpendicular pair) to move the corridors to other sides. Add `up` for a "trinary tree" in 3D.

---

## 4.2 Sidewinder

**Idea.** Work **row by row**. Walk east along the row, building a **run** of cells linked together. At each cell flip a coin:

- *continue*: link to the east cell, the run grows;
- *close out*: pick **one random cell of the run**, carve north from it, then start a new run.

At the east end of a row, always close out. In the top row you cannot carve north, so the whole row becomes one corridor.

**Texture / bias.** One unbroken corridor across the top. A vertical flavour: every run has exactly one way north, so going up is easy, going down is harder. Three of four 2×2 mazes are reachable.

**Cost.** `O(n)`; memory is one row. **Works on masks?** No.

```python
class Sidewinder(MazeAlgorithm):
    """Group cells into runs, then carve north from one cell of each."""

    supports_mask = False

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        for row in grid.each_row():
            run: list[Cell] = []
            for cell in row:
                run.append(cell)
                at_east = cell.east is None
                at_north = cell.north is None
                close_out = at_east or (
                    not at_north and rng.randrange(2) == 0)
                if close_out:
                    member = rng.choice(run)
                    if member.north is not None:
                        member.link(member.north)
                    run.clear()
                elif cell.east is not None:
                    cell.link(cell.east)
        return grid
```

---

## 4.3 Aldous-Broder (unbiased random walk)

**Idea.** Start anywhere. Repeatedly move to a **random neighbour**. If that neighbour was **never visited**, link the two cells. Stop when every cell has been visited.

**Texture / bias.** **None.** Every perfect maze is equally likely (a uniform spanning tree).

**Cost.** Fast at the start, painfully slow at the end (the walker wanders through visited cells searching for the last unvisited ones). Do not use it on huge mazes.

**How do we know a cell is visited?** A visited cell always has at least one link (`links()` is not empty).

```python
class AldousBroder(MazeAlgorithm):
    """Random walk; link only when stepping onto an unvisited cell."""

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        cell = grid.random_cell()
        unvisited = grid.size() - 1          # the start counts as visited
        while unvisited > 0:
            neighbor = rng.choice(cell.neighbors())
            if not neighbor.links():         # never visited
                cell.link(neighbor)
                unvisited -= 1
            cell = neighbor
        return grid
```

---

## 4.4 Wilson's (unbiased, loop-erased random walk)

**Idea.**

1. Mark one random cell as part of the maze.
2. Pick a random cell **not yet in the maze**. Random-walk from it. Whenever the walk crosses itself, **erase the loop** (cut the path back to the first visit of that cell).
3. When the walk touches a cell already in the maze, **carve the whole path** into the maze.
4. Repeat until every cell is in the maze.

**Texture / bias.** None (also uniform, like Aldous-Broder).

**Cost.** Slow at first (looking for the one cell in the maze), fast at the end: the opposite profile to Aldous-Broder. In practice Wilson's is usually faster overall.

Note that the walk **does not carve while walking**; it only remembers the path, and carves it at the end.

```python
class Wilsons(MazeAlgorithm):
    """Loop-erased random walks."""

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        unvisited = list(grid.each_cell())
        unvisited.remove(rng.choice(unvisited))     # the first maze cell

        while unvisited:
            cell = rng.choice(unvisited)
            path = [cell]
            while cell in unvisited:
                cell = rng.choice(cell.neighbors())
                if cell in path:
                    path = path[:path.index(cell) + 1]   # erase the loop
                else:
                    path.append(cell)
            for here, there in zip(path, path[1:]):
                here.link(there)
                unvisited.remove(here)
        return grid
```

(`cell in unvisited` on a list is `O(n)`. Fine for small mazes. For big ones keep a `set` as well.)

---

## 4.5 Hunt-and-Kill

**Idea.** Two phases that alternate:

- **Kill (walk):** from the current cell, step to a **random unvisited neighbour** and link. Repeat until the walk is stuck.
- **Hunt:** scan the grid from the top-left, row by row, for an **unvisited cell that has a visited neighbour**. Link it to a random visited neighbour and walk again from there.

Stop when the hunt finds nothing.

**Texture / bias.** Long winding corridors ("river") and few dead ends (about 10% of cells instead of about 30%).

**Cost.** Needs no extra memory, but the hunt may rescan cells many times, so it can be slow.

```python
class HuntAndKill(MazeAlgorithm):
    """Random walk that never revisits, then hunt for a new start."""

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        current: Optional[Cell] = grid.random_cell()
        while current is not None:
            fresh = [n for n in current.neighbors() if not n.links()]
            if fresh:
                neighbor = rng.choice(fresh)
                current.link(neighbor)
                current = neighbor
            else:
                current = None
                for cell in grid.each_cell():
                    seen = [n for n in cell.neighbors() if n.links()]
                    if not cell.links() and seen:
                        current = cell
                        current.link(rng.choice(seen))
                        break
        return grid
```

---

## 4.6 Recursive Backtracker (depth-first search)

**Idea.** Same walk as Hunt-and-Kill, but when stuck we do not hunt. We **backtrack**: go back along the path we came by (using a **stack**) until we find a cell that still has an unvisited neighbour.

- Push the start on the stack.
- Look at the cell on **top**. If it has unvisited neighbours, choose one, link, **push** it.
- If not, **pop** it (backtrack).
- Stop when the stack is empty.

**Texture / bias.** Very long winding passages, few dead ends (about 10%), a very long solution, few intersections. Visually it looks like a river. This is the best-known "good looking" algorithm.

**Cost.** Visits each cell exactly twice, so it is fast. It needs a stack that can hold every cell.

**Why not real recursion?** Python's default recursion limit is about 1000 calls; a 100×100 maze would crash. An explicit stack (a list) has no such limit. It is also the same algorithm as "depth-first search".

```python
class RecursiveBacktracker(MazeAlgorithm):
    """Depth-first carving with an explicit stack."""

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        stack = [grid.random_cell()]
        while stack:
            current = stack[-1]
            fresh = [n for n in current.neighbors() if not n.links()]
            if not fresh:
                stack.pop()                  # dead end: backtrack
            else:
                neighbor = rng.choice(fresh)
                current.link(neighbor)
                stack.append(neighbor)
        return grid
```

**Hunt-and-Kill or Backtracker?** Same look. Backtracker is faster; Hunt-and-Kill uses less memory.

---

## 4.7 Kruskal's (randomized)

**Origin.** Joseph Kruskal's algorithm for minimum spanning trees: sort all possible passages by cost and take the cheapest ones that do not create a loop.

**Maze version.** Costs do not matter, so just **shuffle** all possible passages.

1. Give each cell **its own set** (a numbered group). A set is a "mini-maze".
2. Make a list of all **neighbour pairs** (each pair once) and shuffle it.
3. For each pair: if the two cells are in **different sets**, link them and **merge the sets**. If they are in the same set, **skip** (linking them would create a loop).
4. When one set is left, you are done.

**Texture / bias.** Almost unbiased, very regular and uniform. Slightly more dead ends than the unbiased algorithms.

**Great for:** starting from a **partly built maze** (pre-merged sets), for example weave crossings or templates.

```python
class Kruskals(MazeAlgorithm):
    """Shuffle all walls; remove a wall if it joins two different sets."""

    def generate(self, grid: Grid) -> Grid:
        set_of: dict[Cell, int] = {}
        members: dict[int, list[Cell]] = {}
        pairs: list[tuple[Cell, Cell]] = []

        for number, cell in enumerate(grid.each_cell()):
            set_of[cell] = number
            members[number] = [cell]
            if cell.south is not None:
                pairs.append((cell, cell.south))
            if cell.east is not None:
                pairs.append((cell, cell.east))

        grid.rng.shuffle(pairs)
        for left, right in pairs:
            if set_of[left] == set_of[right]:
                continue                       # would create a loop
            left.link(right)
            winner, loser = set_of[left], set_of[right]
            for cell in members.pop(loser):    # merge the two sets
                set_of[cell] = winner
                members[winner].append(cell)
        return grid
```

(The professional version of the "which set?" bookkeeping is called **Union-Find** (disjoint set union). The dictionaries above are the simple beginner version.)

---

## 4.8 Prim's, simplified and "true"

**Origin.** Another minimum spanning tree algorithm. It grows **one blob** outward from a starting cell, always adding the cheapest passage touching the blob.

### Simplified Prim's

All passages cost the same, so "cheapest" becomes "random". Keep a list of **active** cells. Pick one at random, link it to a random unvisited neighbour (and make that neighbour active). If it has no unvisited neighbour, remove it from the active list.

- **Texture:** a radial "shattered glass" pattern around the start, many dead ends, short paths.

```python
class SimplifiedPrims(MazeAlgorithm):
    """Grow from a random active cell."""

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        active = [grid.random_cell()]
        while active:
            cell = rng.choice(active)
            fresh = [n for n in cell.neighbors() if not n.links()]
            if fresh:
                neighbor = rng.choice(fresh)
                cell.link(neighbor)
                active.append(neighbor)
            else:
                active.remove(cell)
        return grid
```

### True Prim's

Give every **cell a random cost** (0 to 99). Always pick the **cheapest** active cell, and its **cheapest** unvisited neighbour.

- **Texture:** the radial pattern disappears. A "jigsaw" look, many dead ends (around 45%+), short paths. Similar to Kruskal's.

```python
class TruePrims(MazeAlgorithm):
    """Grow from the cheapest active cell (costs are random)."""

    def generate(self, grid: Grid) -> Grid:
        costs = {c: grid.rng.randrange(100) for c in grid.each_cell()}
        active = [grid.random_cell()]
        while active:
            cell = min(active, key=lambda c: costs[c])
            fresh = [n for n in cell.neighbors() if not n.links()]
            if fresh:
                neighbor = min(fresh, key=lambda c: costs[c])
                cell.link(neighbor)
                active.append(neighbor)
            else:
                active.remove(cell)
        return grid
```

(A priority queue, `heapq`, would make `min` much faster on big grids.)

---

## 4.9 Growing Tree (the "master" algorithm)

**Idea.** The two Prim's versions are almost the same code. They differ only in **how a cell is chosen from the active list**. Growing Tree makes that choice a **pluggable function**:

| Selection rule | You get... |
|---|---|
| random cell | Simplified Prim's |
| **newest** cell (last) | Recursive Backtracker |
| cheapest cell | True Prim's |
| mix: 50% newest / 50% random | Something in between (twisty with some branching) |
| oldest cell (first) | Long straight-ish passages with a radial flavour |

It is like a slider: choose "newest" more often for longer passages; choose "random" more often for more dead ends.

This is the **strategy pattern** in its purest form.

```python
Selector = Callable[[list[Cell], random.Random], Cell]


def pick_last(active: list[Cell], rng: random.Random) -> Cell:
    """Newest cell: behaves like the Recursive Backtracker."""
    return active[-1]


def pick_random(active: list[Cell], rng: random.Random) -> Cell:
    """Random cell: behaves like Simplified Prim's."""
    return rng.choice(active)


def pick_mix(active: list[Cell], rng: random.Random) -> Cell:
    """Half newest, half random."""
    return active[-1] if rng.randrange(2) == 0 else rng.choice(active)


class GrowingTree(MazeAlgorithm):
    """Generic frontier algorithm; *selector* decides the texture."""

    def __init__(self, selector: Selector = pick_last) -> None:
        self.selector = selector

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        active = [grid.random_cell()]
        while active:
            cell = self.selector(active, rng)
            fresh = [n for n in cell.neighbors() if not n.links()]
            if fresh:
                neighbor = rng.choice(fresh)
                cell.link(neighbor)
                active.append(neighbor)
            else:
                active.remove(cell)
        return grid
```

```python
maze = Grid(10, 10, seed=3)
GrowingTree(pick_mix).generate(maze)
```

---

## 4.10 Eller's (row by row with sets)

**Idea.** A child of Sidewinder and Kruskal's. Process **one row at a time**, remembering a set id for each cell of the current row (cells in the same set are already connected).

For each row:

1. Cells without a set get a **new** set id.
2. Look at each pair of east-west neighbours. If they are in **different sets**, randomly link them (coin flip) and merge the sets. In the **last row**, always link when sets differ.
3. For **each set** in the row, carve south from **at least one** cell (pick randomly, and give each extra cell a smaller chance, for example 1 in 3). The cell below inherits the set id. If a set got no southward link it would be cut off from the rest, and that would break the maze.
4. Move to the next row, keeping only the inherited set ids.

**Texture / bias.** Much less biased than Sidewinder. Slight preference for vertical passages.

**Cost.** `O(n)`, memory of **one row**. That means it can generate an **infinitely long** maze (never "finish" the last row).

**Works on masks?** No.

```python
class Ellers(MazeAlgorithm):
    """Row-by-row generation with sets."""

    supports_mask = False

    def generate(self, grid: Grid) -> Grid:
        rng = grid.rng
        columns = grid.columns
        next_id = 0
        sets = [-1] * columns            # set id per column; -1 = none yet

        for row_number, row in enumerate(grid.each_row()):
            last_row = row_number == grid.rows - 1

            for c in range(columns):     # 1. new sets for new cells
                if sets[c] == -1:
                    sets[c] = next_id
                    next_id += 1

            for c in range(columns - 1):  # 2. link east, merge sets
                if sets[c] != sets[c + 1] and (
                        last_row or rng.randrange(2) == 0):
                    row[c].link(row[c + 1])
                    old, new = sets[c + 1], sets[c]
                    sets = [new if s == old else s for s in sets]

            if last_row:
                break

            groups: dict[int, list[int]] = {}   # 3. carve south
            for c, set_id in enumerate(sets):
                groups.setdefault(set_id, []).append(c)
            next_sets = [-1] * columns
            for set_id, cols in groups.items():
                rng.shuffle(cols)
                for position, c in enumerate(cols):
                    south = row[c].south
                    if south is not None and (
                            position == 0 or rng.randrange(3) == 0):
                        row[c].link(south)
                        next_sets[c] = set_id
            sets = next_sets
        return grid
```

---

## 4.11 Recursive Division (wall adder)

**Idea.** Opposite of everything above. Start with an **open room** (every neighbour linked, no inner walls). Then:

1. **Divide** the area with a straight wall (horizontal or vertical), leaving **exactly one gap** in it.
2. Repeat inside each of the two new areas, recursively.
3. Stop when an area is one cell wide or tall.

Choose horizontal when the area is taller than wide, vertical otherwise. That keeps the pieces roughly square.

**Texture / bias.** A boxy, "fractal" texture. Easy to solve: the single gap in each wall is a **bottleneck** you must pass through.

**Rooms trick.** If you randomly stop the recursion early on small areas, those areas stay open: you get **rooms**, like a floor plan.

**Works on masks?** No.

```python
class RecursiveDivision(MazeAlgorithm):
    """Start open, add walls with one gap each."""

    supports_mask = False

    def generate(self, grid: Grid) -> Grid:
        for cell in grid.each_cell():
            for neighbor in cell.neighbors():
                cell.link(neighbor, False)
        self._divide(grid, 0, 0, grid.rows, grid.columns)
        return grid

    def _divide(self, grid: Grid, row: int, column: int,
                height: int, width: int) -> None:
        if height <= 1 or width <= 1:
            return
        rng = grid.rng
        if height > width:                       # horizontal wall
            gap = rng.randrange(width)
            wall_after = rng.randrange(height - 1)
            for x in range(width):
                if x == gap:
                    continue
                cell = grid.at(row + wall_after, column + x)
                if cell.south is not None:
                    cell.unlink(cell.south)
            self._divide(grid, row, column, wall_after + 1, width)
            self._divide(grid, row + wall_after + 1, column,
                         height - wall_after - 1, width)
        else:                                    # vertical wall
            gap = rng.randrange(height)
            wall_after = rng.randrange(width - 1)
            for y in range(height):
                if y == gap:
                    continue
                cell = grid.at(row + y, column + wall_after)
                if cell.east is not None:
                    cell.unlink(cell.east)
            self._divide(grid, row, column, height, wall_after + 1)
            self._divide(grid, row, column + wall_after + 1,
                         height, width - wall_after - 1)
```

Rooms variant: at the top of `_divide`, also `return` when `height < 5 and width < 5 and rng.randrange(4) == 0`.

---

## 4.12 Algorithm registry (strategy pattern in action)

```python
ALGORITHMS: dict[str, type[MazeAlgorithm]] = {
    "binary_tree": BinaryTree,
    "sidewinder": Sidewinder,
    "aldous_broder": AldousBroder,
    "wilsons": Wilsons,
    "hunt_and_kill": HuntAndKill,
    "recursive_backtracker": RecursiveBacktracker,
    "kruskals": Kruskals,
    "prims": SimplifiedPrims,
    "true_prims": TruePrims,
    "growing_tree": GrowingTree,
    "ellers": Ellers,
    "recursive_division": RecursiveDivision,
}


def make_algorithm(name: str) -> MazeAlgorithm:
    """Build an algorithm from its name (used by the config file)."""
    try:
        return ALGORITHMS[name.strip().lower()]()
    except KeyError:
        known = ", ".join(sorted(ALGORITHMS))
        raise ValueError(f"unknown algorithm {name!r} (known: {known})")
```

## 4.13 Which algorithm should I pick?

| Need | Choose |
|---|---|
| Best looking, long solution, few dead ends | Recursive Backtracker (or Hunt-and-Kill) |
| Mathematically fair mazes | Wilson's (or Aldous-Broder) |
| Fastest and simplest | Binary Tree, Sidewinder |
| Memory-light / infinite | Eller's |
| Control the texture with one parameter | Growing Tree |
| Pre-placed pieces (weaves, templates) | Kruskal's |
| Rooms and floor plans | Recursive Division |
| **Mask with a hidden "42"** | Backtracker, Hunt-and-Kill, Wilson's, Aldous-Broder, Kruskal's, Prim's, Growing Tree (*not* Binary Tree, Sidewinder, Eller's, Recursive Division) |

---

# Part 5: Solving, Measuring, Coloring

## 5.1 Distances (breadth-first search / simplified Dijkstra)

Dijkstra's algorithm measures the distance from **one starting cell** to **every other cell**. When every step costs 1, it is "flood fill": imagine water poured at the start cell.

1. Start cell: distance 0.
2. The **frontier** is the set of cells just reached. Give their unvisited linked neighbours distance + 1; they become the new frontier.
3. Repeat until nobody is left.

With a queue (`deque`) this is called **breadth-first search (BFS)**.

```python
class Distances:
    """Distance from a root cell to every reachable cell."""

    def __init__(self, root: Cell) -> None:
        self.root = root
        self._cells: dict[Cell, int] = {root: 0}

    def __getitem__(self, cell: Cell) -> int:
        return self._cells[cell]

    def __setitem__(self, cell: Cell, distance: int) -> None:
        self._cells[cell] = distance

    def __contains__(self, cell: object) -> bool:
        return cell in self._cells

    def __len__(self) -> int:
        return len(self._cells)

    def items(self) -> Iterator[tuple[Cell, int]]:
        return iter(self._cells.items())

    def farthest(self) -> tuple[Cell, int]:
        """The cell with the largest distance, and that distance."""
        return max(self._cells.items(), key=lambda item: item[1])

    def path_to(self, goal: Cell) -> list[Cell]:
        """Shortest path root -> goal (walk backwards, distance - 1)."""
        if goal not in self._cells:
            raise ValueError("goal is not reachable from the root")
        current = goal
        path = [current]
        while current is not self.root:
            for neighbor in current.links():
                if self._cells[neighbor] < self._cells[current]:
                    current = neighbor
                    path.append(current)
                    break
        path.reverse()
        return path


def compute_distances(root: Cell) -> Distances:
    """Breadth-first flood fill from *root* (all steps cost 1)."""
    distances = Distances(root)
    frontier = deque([root])
    while frontier:
        cell = frontier.popleft()
        for linked in cell.links():
            if linked in distances:
                continue
            distances[linked] = distances[cell] + 1
            frontier.append(linked)
    return distances
```

**Finding the shortest path** = start at the goal, repeatedly step to a linked neighbour whose distance is **one less**, until you reach distance 0. That is `path_to`. It is guaranteed shortest.

## 5.2 Turning a path into `N`/`E`/`S`/`W` letters

```python
def path_directions(path: list[Cell]) -> str:
    """Letters describing each step of a path (needed for the output)."""
    letters: list[str] = []
    for here, there in zip(path, path[1:]):
        if there is here.north:
            letters.append("N")
        elif there is here.east:
            letters.append("E")
        elif there is here.south:
            letters.append("S")
        elif there is here.west:
            letters.append("W")
        else:
            raise ValueError("cells are not adjacent")
    return "".join(letters)
```

## 5.3 Showing distances in the terminal

```python
grid = Grid(5, 5, seed=7)
RecursiveBacktracker().generate(grid)
distances = compute_distances(grid.at(0, 0))


def last_digit_base36(number: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    return digits[number % 36]          # one character per cell


grid.labels = {cell: last_digit_base36(d) for cell, d in distances.items()}
print(grid)
```

`grid.labels` feeds the `contents_of` hook, which `__str__` calls for each cell.

## 5.4 Making a maze harder: the longest path

A longer solution is usually a harder maze. Trick: **run BFS twice**.

1. From any cell, find the farthest cell `A`.
2. From `A`, find the farthest cell `B`.
3. The path `A → B` is a longest path in the maze.

Why twice? The farthest cell from an arbitrary start is always one *end* of a longest path in a tree. In a general graph this problem is "NP-hard" (very hard), but in a **tree** (perfect maze) the double-BFS trick is exact. This longest path is called the tree's **diameter**.

```python
def longest_path(grid: Grid) -> list[Cell]:
    """A longest path through a perfect maze (two BFS passes)."""
    start = grid.random_cell()
    far, _ = compute_distances(start).farthest()
    distances = compute_distances(far)
    goal, _ = distances.farthest()
    return distances.path_to(goal)
```

Put the entrance at one end and the exit at the other.

## 5.5 Cost versus distance (weighted Dijkstra)

If cells have different costs (lava = 50, normal = 1), the "flood" idea breaks: the flood may reach the goal through the short but expensive route first.

The real Dijkstra fixes this: **always process the cheapest unprocessed cell first**. Use a **priority queue** (`heapq`).

```python
def dijkstra(root: Cell, weight: Callable[[Cell], int]) -> Distances:
    """Cheapest cost from *root* to every cell (weight = cost to enter)."""
    costs = Distances(root)
    tie = itertools.count()              # Cells cannot be compared
    heap: list[tuple[int, int, Cell]] = [(0, next(tie), root)]
    while heap:
        cost, _, cell = heapq.heappop(heap)
        if cost > costs[cell]:
            continue                      # an older, worse entry
        for neighbor in cell.links():
            total = cost + weight(neighbor)
            if neighbor not in costs or total < costs[neighbor]:
                costs[neighbor] = total
                heapq.heappush(heap, (total, next(tie), neighbor))
    return costs
```

`path_to` must then be replaced by "walk back to the neighbour with the smaller *cost*"; the idea is identical. Weighted Dijkstra also works on **braid** (looped) mazes, which simple BFS handles only when all costs are equal.

## 5.6 Coloring mazes (an X-ray of the algorithm)

Turn each distance into a color intensity: farthest cells darkest, the start lightest. Looking at a colored maze reveals its texture and the algorithm's bias: diagonal stripes for Binary Tree, vertical stripes for Sidewinder, a long snake for the Backtracker, a radial burst for Simplified Prim's, a boxy pixel look for Recursive Division.

```python
# snippet  (pseudocode for an image library such as Pillow)
intensity = (maximum - distance) / maximum        # 1.0 at the start
dark = round(255 * intensity)
bright = 128 + round(127 * intensity)
color = (dark, bright, dark)                       # shades of green
```

## 5.7 Measuring a maze

```python
def is_perfect(grid: Grid) -> bool:
    """True if every cell is reachable and there is no loop."""
    cells = list(grid.each_cell())
    if not cells:
        return True
    edges = sum(len(c.links()) for c in cells) // 2
    reached = compute_distances(cells[0])
    return len(reached) == len(cells) and edges == len(cells) - 1
```

Reminder: for a perfect maze with `n` cells, `edges == n - 1` and everything is reachable.

---

# Part 6: Displaying a Maze

## 6.1 ASCII art

You already have it: `print(grid)` uses `+`, `-` and `|`. The trick that makes it simple: **each cell draws only its own east and south walls**. The north wall is the south wall of the cell above, and the west wall is the east wall of the cell on the left. Only the very first top line and left column need special drawing.

## 6.2 Colored terminal output (ANSI escape codes)

An escape code like `"\033[36m"` switches the terminal color; `"\033[0m"` resets it.

```python
# a_maze_ing.py (display part)
RESET = "\033[0m"
WALL_COLORS = ["\033[37m", "\033[36m", "\033[32m", "\033[35m", "\033[33m"]
ENTRY_COLOR = "\033[35m"
EXIT_COLOR = "\033[31m"
PATH_COLOR = "\033[33m"
LOGO_COLOR = "\033[34m"


def paint(text: str, color: str) -> str:
    """Wrap *text* in an ANSI color."""
    return f"{color}{text}{RESET}" if color else text
```

The full `render()` function is in Part 10 because it needs the `MazeGenerator`.

## 6.3 Other ways to draw (ideas from the book)

- A PNG image with a library such as Pillow (draw lines for walls, filled rectangles for colors).
- SVG or PDF, an HTML canvas, or the MiniLibX graphical library (A-Maze-ing allows it).
- **Inset walls:** leave a gap between corridors so that walls have thickness. This is essential for weave mazes.
- **Tiles:** pre-draw the 16 possible cell shapes and paste them.

---

# Part 7: Fitting Mazes to Shapes (Masking)

## 7.1 The idea

Treat the grid like a low-resolution picture. Each cell is a pixel that can be **on** or **off**. Turn some cells **off** and the algorithm never visits them. Your maze takes the shape of the "on" area. This is exactly how to make the **"42"** in A-Maze-ing.

Our `Cell.detach()` already does it: it disconnects the cell from the grid and marks it `blocked`. The neighbours then think the cell does not exist.

## 7.2 Consequences and warnings

- Algorithms that depend on the rectangular shape fail on masks: **Binary Tree, Sidewinder, Eller's, Recursive Division**. Their `supports_mask` is `False`.
- Algorithms based on `neighbors()` work fine: Backtracker, Hunt-and-Kill, Wilson's, Aldous-Broder, Kruskal's, Prim's, Growing Tree.
- The "on" area must be **connected**. If a region is cut off from the rest, no algorithm can join it and the maze will not be fully connected (or the algorithm may fail).
- Masks create jagged edges on circles and diagonals. For circles use polar grids (Part 9).

## 7.3 Masks from text drawings

```python
def blocked_from_text(drawing: str) -> list[tuple[int, int]]:
    """Cells to block: every 'X' in a text drawing (row, column)."""
    lines = [line.strip() for line in drawing.strip().splitlines()]
    return [(r, c)
            for r, line in enumerate(lines)
            for c, char in enumerate(line)
            if char == "X"]


SHAPE = """
X.......X
.........
....X....
.........
X.......X
"""
cells = blocked_from_text(SHAPE)
shaped = Grid(5, 9, seed=5, blocked=cells)
RecursiveBacktracker().generate(shaped)
print(shaped)
```

## 7.4 The "42" pattern

Draw "4" and "2" with a 3×5 pixel font and a blank column between them:

```text
X.X.XXX
X.X...X
XXX.XXX
..X.X..
..X.XXX
```

Place it in the middle of the maze. Rules we follow:

- **Needs at least a 1-cell margin** on every side, so the open pockets of the glyphs (for example the notch at the top of the "4") are still connected to the rest. So the maze must be at least **9 columns × 7 rows**.
- If the maze is too small, **print an error message and omit the pattern** (A-Maze-ing requires this message).
- The blocked cells keep **all four walls closed** (hex digit `F`).

```python
FORTY_TWO = (
    "X.X.XXX",
    "X.X...X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX",
)


def logo_cells(rows: int, columns: int) -> Optional[set[tuple[int, int]]]:
    """(row, column) cells of the '42' centred in the maze, or None if
    the maze is too small (a margin of at least 1 cell is required)."""
    height, width = len(FORTY_TWO), len(FORTY_TWO[0])
    if rows < height + 2 or columns < width + 2:
        return None
    top = (rows - height) // 2
    left = (columns - width) // 2
    return {(top + r, left + c)
            for r, line in enumerate(FORTY_TWO)
            for c, char in enumerate(line)
            if char == "X"}
```

(The exact glyph shape is my design. The subject only says the closed cells must form a visible "42". Feel free to design your own.)

---

# Part 8: Loops, Braids and the "No Wide Rooms" Rule

## 8.1 Braiding (dead-end removal)

To make a non-perfect maze: for each **dead end**, link it to one more neighbour. That erases a wall and creates a loop. A parameter `p` between 0 and 1 gives the fraction of dead ends to remove: `p = 1.0` is a full braid maze, `p = 0.3` a lightly braided one.

Nice trick: prefer linking two dead ends together, which removes two dead ends with one wall.

## 8.2 A guard against wide-open areas

A-Maze-ing forbids open blocks of **3×3 cells** (corridors may be at most 2 wide). A *perfect* maze can never contain even a 2×2 open block (that would be a loop), so only braiding can cause the problem. The guard: after each new link, check whether it created a 3×3 open block, and take it back if so. Taking back a link that we just *added* never disconnects the maze.

```python
def is_open_block(grid: Grid, top: int, left: int, size: int = 3) -> bool:
    """True if all inner walls of a size x size block are removed."""
    for r in range(top, top + size):
        for c in range(left, left + size):
            cell = grid.at(r, c)
            if c < left + size - 1 and not cell.is_linked(cell.east):
                return False
            if r < top + size - 1 and not cell.is_linked(cell.south):
                return False
    return True


def has_open_block(grid: Grid, size: int = 3) -> bool:
    """True if the maze contains a size x size fully open block."""
    return any(is_open_block(grid, r, c, size)
               for r in range(grid.rows - size + 1)
               for c in range(grid.columns - size + 1))


def braid(grid: Grid, p: float = 1.0, avoid_open_block: bool = True) -> None:
    """Remove dead ends by adding loops."""
    rng = grid.rng
    ends = grid.deadends()
    rng.shuffle(ends)
    for cell in ends:
        if len(cell.links()) != 1 or rng.random() > p:
            continue
        candidates = [n for n in cell.neighbors() if not cell.is_linked(n)]
        best = [n for n in candidates if len(n.links()) == 1]
        pool = best or candidates
        if not pool:
            continue
        neighbor = rng.choice(pool)
        cell.link(neighbor)
        if avoid_open_block and has_open_block(grid):
            cell.unlink(neighbor)
```

(This reading of "3×3 open" is my interpretation: all 12 inner walls removed. Check your subject and the provided checker if it is stricter.)

## 8.3 Dijkstra and loops

A braid maze has several routes between two cells. The BFS distances still work, and `path_to` picks one shortest route.

---

# Part 9: Other Grids and Shapes (Theory + Code)

Because `_prepare_grid` and `_configure_cells` are separate methods, a new grid shape only needs to override them. Algorithms keep working as long as they use `neighbors()` and `links()`.

(The blocks in this part are runnable, but their type hints are simplified for readability.)

## 9.1 Hexagon grids ("sigma" mazes)

A flat-topped hexagon has **6** neighbours: N, S, NE, NW, SE, SW. Store the grid as a normal 2D array of columns, where the odd columns are pushed down half a hexagon. Therefore the diagonal neighbours of **even columns** are in the row above (`north diagonal = row - 1`) and the row itself (`south diagonal = row`); for **odd columns** they are in the row itself and the row below.

```python
# advanced
class HexCell(Cell):
    """A hexagon: six neighbours instead of four."""

    def __init__(self, row: int, column: int) -> None:
        super().__init__(row, column)
        self.northeast: Optional[Cell] = None
        self.northwest: Optional[Cell] = None
        self.southeast: Optional[Cell] = None
        self.southwest: Optional[Cell] = None

    def neighbors(self) -> list[Cell]:
        around = (self.northwest, self.north, self.northeast,
                  self.southwest, self.south, self.southeast)
        return [cell for cell in around if cell is not None]


class HexGrid(Grid):
    """Grid of hexagons (flat-topped, zig-zag rows)."""

    def _prepare_grid(self) -> list[list[Cell]]:
        return [[HexCell(r, c) for c in range(self.columns)]
                for r in range(self.rows)]

    def _configure_cells(self) -> None:
        for cell in self.each_cell():
            row, col = cell.row, cell.column
            if col % 2 == 0:
                north_diag, south_diag = row - 1, row
            else:
                north_diag, south_diag = row, row + 1
            cell.northwest = self[north_diag, col - 1]   # type: ignore
            cell.north = self[row - 1, col]
            cell.northeast = self[north_diag, col + 1]   # type: ignore
            cell.southwest = self[south_diag, col - 1]   # type: ignore
            cell.south = self[row + 1, col]
            cell.southeast = self[south_diag, col + 1]   # type: ignore
```

Drawing facts: for hexagons with side `s`, the width is `2s`, the height is `s·√3`, and the horizontal spacing between columns is `1.5 s`.

Binary Tree and Sidewinder want "east", which does not exist. Use "next column in the same row": `grid[row, column + 1]`.

## 9.2 Triangle grids ("delta" mazes)

Triangles alternate pointing up and down. A triangle is **upright** if `(row + column)` is even. An upright triangle has no north neighbour (it has a south neighbour); an upside-down one has no south neighbour (it has a north neighbour). Everyone has east and west neighbours.

```python
# advanced
class TriangleGrid(Grid):
    """Alternating up/down triangles."""

    def _configure_cells(self) -> None:
        for cell in self.each_cell():
            row, col = cell.row, cell.column
            cell.west = self[row, col - 1]
            cell.east = self[row, col + 1]
            if (row + col) % 2 == 0:             # upright
                cell.south = self[row + 1, col]
            else:
                cell.north = self[row - 1, col]
```

Drawing facts for triangle side `s`: height `s·√3/2`.

Other tilings that work: octagons + squares ("upsilon" mazes), and any shape that tiles the plane.

## 9.3 Polar grids ("theta" or circle mazes)

A polar grid is rings (rows) cut into wedges (cells).

- A cell is described by an **inner radius**, an **outer radius**, and two angles (counter-clockwise edge and clockwise edge). With `cell_count` cells in a ring, `theta = 2π / cell_count`.
- Polar to Cartesian: `x = r·cos(θ)`, `y = r·sin(θ)`. Remember "cosine comes before sine, like x before y".
- Problem: outer rings have wide cells. Fix by **adaptive subdivision**: when a cell becomes about 1.5× wider than the ring is tall, split every cell of the next ring in two. A cell then may have **two outward neighbours**.
- Add the "wrap-around" (column modulo the row length) so the last wedge touches the first one. Otherwise you get an ugly seam.

```python
# advanced
class PolarCell(Cell):
    """Cell of a ring: clockwise, counter-clockwise, inward, outward."""

    def __init__(self, row: int, column: int) -> None:
        super().__init__(row, column)
        self.cw: Optional[PolarCell] = None
        self.ccw: Optional[PolarCell] = None
        self.inward: Optional[PolarCell] = None
        self.outward: list[PolarCell] = []

    def neighbors(self) -> list[Cell]:
        around: list[Optional[Cell]] = [self.cw, self.ccw, self.inward]
        return [c for c in around if c is not None] + list(self.outward)


class PolarGrid(Grid):
    """Concentric rings; ring 0 is a single cell in the centre."""

    def __init__(self, rows: int, seed: Optional[int] = None) -> None:
        super().__init__(rows, 1, seed)

    def _prepare_grid(self) -> list[list[Cell]]:
        rings: list[list[Cell]] = [[PolarCell(0, 0)]]
        row_height = 1.0 / self.rows
        for row in range(1, self.rows):
            radius = row / self.rows
            circumference = 2 * math.pi * radius
            previous = len(rings[row - 1])
            estimated_width = circumference / previous
            # int(x + 0.5): school rounding (Python's round() rounds
            # halves to the nearest even number).
            ratio = int(estimated_width / row_height + 0.5)
            rings.append([PolarCell(row, c) for c in range(previous * ratio)])
        return rings

    def __getitem__(self, position: tuple[int, int]) -> Optional[Cell]:
        row, column = position
        if not 0 <= row < self.rows:
            return None
        ring = self._grid[row]
        return ring[column % len(ring)]            # wrap around

    def _configure_cells(self) -> None:
        for cell in self.each_cell():
            row, col = cell.row, cell.column
            if row > 0:
                cell.cw = self[row, col + 1]                # type: ignore
                cell.ccw = self[row, col - 1]               # type: ignore
                ratio = len(self._grid[row]) // len(self._grid[row - 1])
                parent = self._grid[row - 1][col // ratio]
                parent.outward.append(cell)                 # type: ignore
                cell.inward = parent                        # type: ignore
```

## 9.4 Weave mazes (passages over and under)

Passages cross over and under each other. Four rules keep them unambiguous:

1. A passage cannot **dead-end** while over or under another.
2. Over and under passages must be **perpendicular**.
3. A passage cannot **turn** while above or below another.
4. A passage cannot tunnel under **two consecutive** passages (to keep the code simple).

Implementation idea: a tunnel is a hidden **under-cell** at the same coordinates as an **over-cell**. The grid creates under-cells on demand when two cells on both sides of a straight corridor are linked "through" it. Drawing needs **inset walls** (gaps between corridors).

```python
# snippet
def can_tunnel_north(cell):
    """North neighbour is a horizontal corridor and there is a cell
    behind it."""
    north = cell.north
    return (north is not None and north.north is not None
            and north.is_horizontal_passage())     # linked E+W, not N+S
```

**Reliable weaves with Kruskal's.** Plain random weaving may produce zero crossings. Better: *place* the crossings first (only on cells that are still unlinked), each crossing gives pre-merged sets, then run Kruskal's to fill in the rest. You control the density: more crossings equals a denser weave. The same trick works for any template (spirals, rooms, ...).

## 9.5 Three and four dimensions

Add a coordinate. For 3D you add `level`, plus two neighbours: `up` and `down`.

```python
# advanced
class Cell3D(Cell):
    """A cell with levels."""

    def __init__(self, level: int, row: int, column: int) -> None:
        super().__init__(row, column)
        self.level = level
        self.up: Optional[Cell] = None
        self.down: Optional[Cell] = None

    def neighbors(self) -> list[Cell]:
        extra = [c for c in (self.up, self.down) if c is not None]
        return super().neighbors() + extra
```

`Grid3D` has a 3D list `grid[level][row][column]`, an accessor `grid[level, row, column]`, and overrides `_prepare_grid`, `_configure_cells`, `each_row`, `size`. Display it as floor plans side by side with arrows for stairs.

Important: **do not** make a 3D maze by stacking perfect 2D mazes and adding several ladders. Each extra ladder creates a loop. Generate on the real 3D grid instead and the result stays perfect. Binary Tree becomes a "trinary tree" (north, east, up). Four dimensions add "hither/yon".

## 9.6 Planair mazes (on surfaces)

- **Cylinder:** an ordinary grid whose columns **wrap around**. Override `__getitem__` so that `column % columns`.
- **Möbius strip:** a cylinder with a half-twist, so you must draw the maze on **both sides** of the strip: generate a long grid, cut it in two halves, print both halves one below the other, fold along the middle, twist, and tape.
- **Cube:** six square faces stored as six small grids. The hard part is a `wrap()` table that says where you land when you walk off an edge (for example east off face 4 lands on the top edge of face 2).
- **Sphere:** two hemispheres, each a polar-grid variant, glued at the equator. Draw the maze on a flat map (like a world map, where the poles are stretched) and let a ray tracer (POV-Ray) wrap it around a sphere.

```python
# advanced
class CylinderGrid(Grid):
    """Left and right edges are neighbours."""

    def __getitem__(self, position: tuple[int, int]) -> Optional[Cell]:
        row, column = position
        if not 0 <= row < self.rows:
            return None
        return self._grid[row][column % self.columns]
```

---

# Part 10: Building A-Maze-ing, Step by Step

## 10.1 Requirements → concepts

| Requirement of the subject | Concept / code in this guide |
|---|---|
| Maze from `WIDTH`, `HEIGHT` | `Grid(rows=HEIGHT, columns=WIDTH)` |
| Reproducible with a seed | `random.Random(seed)` inside `Grid`; `dict` insertion order |
| Connected (except the "42") | Spanning tree algorithms + blocked cells |
| `PERFECT=True` → exactly one path | Spanning tree = perfect maze (Part 1.3) |
| `PERFECT=False` | `braid()` |
| No 3×3 open areas | `has_open_block()` guard in `braid` |
| Walls on the border | Cells have no neighbour outside → always closed |
| Coherent walls between neighbours | `Cell.link` is bidirectional |
| Hidden "42" | Mask (Part 7.4); print an error if too small |
| Shortest path as `N/E/S/W` | `compute_distances` + `path_to` + `path_directions` |
| One hex digit per cell | Bitmask encoding (below) |
| Terminal or MLX display | `render()` (below) |
| Re-generate / show path / colors | `interactive()` (below) |
| Reusable module | `mazegen` package with `MazeGenerator` |
| Graceful errors | `ConfigError`, `try/except` in `main` |

## 10.2 The hex output format

Each cell becomes one hex digit made of four bits. **A bit set to 1 means that wall is CLOSED.**

| Bit | Value | Wall |
|---|---|---|
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

Examples:

- `3` = `0011` = North and East closed. So **South and West are open**. Both ways of saying it are the same fact: closed means bit 1, open means bit 0.
- `A` = `1010` = East and West closed (a vertical corridor).
- `F` = all four closed (a "42" cell, or a fully enclosed cell).
- `0` = all four open (a crossroad).

The file layout (every line ends with `\n`):

```text
D53
956
C57

0,0
2,2
EESWWSEE
```

1. One line per row, one hex digit per cell.
2. One **empty line**.
3. Entry as `x,y`.
4. Exit as `x,y`.
5. The shortest path as letters.

The 3×3 snake maze of Part 1.1 encodes exactly to the rows `D53`, `956`, `C57`. Verify one cell by hand: the top-left cell has North (1) closed, South (4) closed, West (8) closed and East open: 1 + 4 + 8 = 13 = `D`.

```python
def encode_cell(cell: Cell) -> str:
    """One hex digit: bit set = wall closed (N=1, E=2, S=4, W=8)."""
    value = 0
    if not cell.is_linked(cell.north):
        value |= 1
    if not cell.is_linked(cell.east):
        value |= 2
    if not cell.is_linked(cell.south):
        value |= 4
    if not cell.is_linked(cell.west):
        value |= 8
    return format(value, "X")
```

`is_linked(None)` is `False`, so a border wall counts as closed automatically.

> **To verify with your subject / checker:** hex letters in uppercase (as in the subject's example `A`), the `(x, y)` convention with `y` going down, and what to write when the entry/exit cell sits on the border (the subject says the outer wall may be open at those points, so you may need to clear that bit for those two cells).

## 10.3 The config file

```text
# config.txt
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
# optional extras (allowed by the subject)
SEED=42
ALGORITHM=recursive_backtracker
```

```python
# a_maze_ing.py (config part)
class ConfigError(Exception):
    """Raised for any problem with the configuration file."""


@dataclass(frozen=True)
class MazeConfig:
    """All settings of one run."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "recursive_backtracker"


MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                  "PERFECT")


def parse_point(text: str, name: str) -> tuple[int, int]:
    """Turn 'x,y' into (x, y)."""
    parts = text.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{name} must look like x,y (got {text!r})")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        raise ConfigError(f"{name} must contain integers (got {text!r})")


def load_config(path: str) -> MazeConfig:
    """Read and validate KEY=VALUE lines ('#' starts a comment)."""
    values: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for number, raw in enumerate(handle, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"line {number}: expected KEY=VALUE, got {line!r}")
                key, value = line.split("=", 1)
                values[key.strip().upper()] = value.strip()
    except OSError as error:
        raise ConfigError(f"cannot read {path!r}: {error}") from error

    missing = [key for key in MANDATORY_KEYS if key not in values]
    if missing:
        raise ConfigError("missing keys: " + ", ".join(missing))

    try:
        width = int(values["WIDTH"])
        height = int(values["HEIGHT"])
        seed = int(values["SEED"]) if "SEED" in values else None
    except ValueError as error:
        raise ConfigError(f"WIDTH, HEIGHT and SEED must be integers: "
                          f"{error}") from error

    flag = values["PERFECT"].lower()
    if flag not in ("true", "false"):
        raise ConfigError("PERFECT must be True or False")

    entry = parse_point(values["ENTRY"], "ENTRY")
    exit_pos = parse_point(values["EXIT"], "EXIT")
    if width < 1 or height < 1:
        raise ConfigError("WIDTH and HEIGHT must be positive")
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_pos)):
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(f"{name} {x},{y} is outside the maze")
    if entry == exit_pos:
        raise ConfigError("ENTRY and EXIT must be different")

    return MazeConfig(
        width=width, height=height, entry=entry, exit_pos=exit_pos,
        output_file=values["OUTPUT_FILE"], perfect=flag == "true",
        seed=seed, algorithm=values.get("ALGORITHM",
                                        "recursive_backtracker"))
```

## 10.4 The reusable class `MazeGenerator`

This is the class that goes into your installable `mazegen` package. It **composes** a `Grid`, an algorithm (strategy) and the helpers above.

```python
# mazegen/generator.py
class MazeGenerator:
    """Generate, solve and export a maze.

    Example:
        >>> maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
        >>> maze.grid           # the Grid of Cells
        >>> maze.solution()     # list of Cells from entry to exit
        >>> maze.hex_rows()     # one hex string per row
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
        algorithm: Optional[MazeAlgorithm] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.perfect = perfect
        self.seed = seed if seed is not None else random.randrange(2**32)
        self.algorithm = algorithm or RecursiveBacktracker()
        self.logo_fits = False
        self.grid = self._build()

    def regenerate(self, seed: Optional[int] = None) -> None:
        """Build a brand new maze (new random seed unless given)."""
        self.seed = seed if seed is not None else random.randrange(2**32)
        self.grid = self._build()

    def _build(self) -> Grid:
        if self.entry == self.exit_pos:
            raise ValueError("entry and exit must be different")
        for name, (x, y) in (("entry", self.entry), ("exit", self.exit_pos)):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"{name} {x},{y} is outside the maze")

        blocked = logo_cells(self.height, self.width)
        self.logo_fits = blocked is not None
        if blocked is None:
            print("Error: the maze is too small to show the 42 pattern; "
                  "it is omitted.", file=sys.stderr)
            blocked = set()
        for name, (x, y) in (("entry", self.entry), ("exit", self.exit_pos)):
            if (y, x) in blocked:                  # (row, column)
                raise ValueError(f"{name} {x},{y} is inside the 42 pattern")
        if blocked and not self.algorithm.supports_mask:
            raise ValueError(
                f"{type(self.algorithm).__name__} cannot be used with "
                "the 42 pattern; pick another algorithm")

        grid = Grid(self.height, self.width, self.seed, blocked)
        self.algorithm.generate(grid)
        if not self.perfect:
            braid(grid, 0.3)
        return grid

    def entry_cell(self) -> Cell:
        return self.grid.at(self.entry[1], self.entry[0])

    def exit_cell(self) -> Cell:
        return self.grid.at(self.exit_pos[1], self.exit_pos[0])

    def solution(self) -> list[Cell]:
        """Shortest path from entry to exit (inclusive)."""
        distances = compute_distances(self.entry_cell())
        return distances.path_to(self.exit_cell())

    def solution_directions(self) -> str:
        """The shortest path as letters N/E/S/W."""
        return path_directions(self.solution())

    def hex_rows(self) -> list[str]:
        """One hexadecimal string per row of the maze."""
        return ["".join(encode_cell(cell) for cell in row)
                for row in self.grid.each_row()]

    def write_output(self, filename: str) -> None:
        """Write the maze in the subject's file format."""
        with open(filename, "w", encoding="utf-8") as handle:
            for line in self.hex_rows():
                handle.write(line + "\n")
            handle.write("\n")
            handle.write(f"{self.entry[0]},{self.entry[1]}\n")
            handle.write(f"{self.exit_pos[0]},{self.exit_pos[1]}\n")
            handle.write(self.solution_directions() + "\n")
```

## 10.5 Terminal display and interaction

```python
# a_maze_ing.py (display and menu)
def render(maze: MazeGenerator, show_path: bool, wall_color: str) -> str:
    """The maze as colored text."""
    grid = maze.grid
    on_path = set(maze.solution()) if show_path else set()
    entry, goal = maze.entry_cell(), maze.exit_cell()
    lines = [paint("+" + "---+" * grid.columns, wall_color)]
    for row in grid.each_row():
        top = paint("|", wall_color)
        bottom = paint("+", wall_color)
        for cell in row:
            if cell.blocked:
                body = paint("###", LOGO_COLOR)
            elif cell is entry:
                body = paint(" S ", ENTRY_COLOR)
            elif cell is goal:
                body = paint(" E ", EXIT_COLOR)
            elif cell in on_path:
                body = paint(" * ", PATH_COLOR)
            else:
                body = "   "
            east = (" " if cell.is_linked(cell.east)
                    else paint("|", wall_color))
            top += body + east
            south = ("   " if cell.is_linked(cell.south)
                     else paint("---", wall_color))
            bottom += south + paint("+", wall_color)
        lines.append(top)
        lines.append(bottom)
    return "\n".join(lines)


def interactive(maze: MazeGenerator, output_file: str) -> None:
    """Menu loop: regenerate, show/hide path, rotate colors, quit."""
    show_path = False
    color_index = 0
    while True:
        print(render(maze, show_path, WALL_COLORS[color_index]))
        print("1. Re-generate  2. Show/Hide path  "
              "3. Rotate colors  4. Quit")
        try:
            choice = input("Choice? (1-4): ").strip()
        except EOFError:
            return
        if choice == "1":
            maze.regenerate()
            maze.write_output(output_file)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
        elif choice == "4":
            return
        else:
            print("Please type a number from 1 to 4.")


def main(argv: list[str]) -> int:
    """Entry point: python3 a_maze_ing.py config.txt"""
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config = load_config(argv[1])
        maze = MazeGenerator(
            config.width, config.height, config.entry, config.exit_pos,
            config.perfect, config.seed, make_algorithm(config.algorithm))
        maze.write_output(config.output_file)
    except (ConfigError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    interactive(maze, config.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

## 10.6 A self-check script for your output file

The subject gives you an official checker. Until you have it, this small function catches the most common mistakes (it is **not** the official one).

```python
def check_output_file(filename: str) -> list[str]:
    """Return a list of problems found in an output file (empty = ok)."""
    problems: list[str] = []
    with open(filename, encoding="utf-8") as handle:
        text = handle.read()
    if not text.endswith("\n"):
        problems.append("the file must end with a newline")
    lines = text.split("\n")
    if "" not in lines:
        return problems + ["no empty line before entry/exit/path"]
    blank = lines.index("")
    rows, tail = lines[:blank], lines[blank + 1:]
    if len(tail) < 3 or not rows:
        return problems + ["missing entry / exit / path lines"]
    if len({len(row) for row in rows}) != 1:
        return problems + ["rows do not all have the same length"]
    try:
        walls = [[int(ch, 16) for ch in row] for row in rows]
        ex, ey = (int(v) for v in tail[0].split(","))
        gx, gy = (int(v) for v in tail[1].split(","))
    except ValueError:
        return problems + ["bad hex digit or bad entry/exit line"]

    height, width = len(walls), len(walls[0])
    for y in range(height):
        for x in range(width):
            value = walls[y][x]
            if x + 1 < width and bool(value & 2) != bool(walls[y][x+1] & 8):
                problems.append(f"incoherent wall: ({x},{y}) / ({x+1},{y})")
            if y + 1 < height and bool(value & 4) != bool(walls[y+1][x] & 1):
                problems.append(f"incoherent wall: ({x},{y}) / ({x},{y+1})")
            border = ((y == 0 and not value & 1)
                      or (y == height - 1 and not value & 4)
                      or (x == 0 and not value & 8)
                      or (x == width - 1 and not value & 2))
            if border and (x, y) not in ((ex, ey), (gx, gy)):
                problems.append(f"open outer wall at ({x},{y})")

    moves = {"N": (0, -1, 1), "E": (1, 0, 2), "S": (0, 1, 4), "W": (-1, 0, 8)}
    x, y = ex, ey
    for letter in tail[2]:
        if letter not in moves:
            problems.append(f"bad path letter {letter!r}")
            break
        dx, dy, bit = moves[letter]
        if walls[y][x] & bit:
            problems.append(f"path crosses a wall at ({x},{y})")
            break
        x, y = x + dx, y + dy
        if not (0 <= x < width and 0 <= y < height):
            problems.append("path leaves the maze")
            break
    else:
        if (x, y) != (gx, gy):
            problems.append("path does not end at the exit")
    return problems
```

## 10.7 `Makefile` (recipe lines start with a TAB, not spaces)

```makefile
PYTHON = python3
MAIN   = a_maze_ing.py
CONFIG = config.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache build dist *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
```

`clean` removes `dist/` but **not** the `mazegen-*.whl` you copied to the repository root (the subject requires it there).

## 10.8 Packaging `mazegen` (my suggested setup)

Layout:

```text
repo/
├── a_maze_ing.py
├── config.txt
├── Makefile
├── README.md
├── pyproject.toml
├── mazegen-1.0.0-py3-none-any.whl     <- copy here after building
└── mazegen/
    ├── __init__.py       # from .generator import MazeGenerator
    ├── cell.py
    ├── grid.py
    ├── algorithms.py
    ├── paths.py          # Distances, compute_distances, path_directions
    └── generator.py
```

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0.0"
description = "Reusable maze generator"
requires-python = ">=3.10"

[tool.setuptools.packages.find]
include = ["mazegen*"]
```

Build and test in a clean environment:

```bash
python3 -m venv /tmp/venv && . /tmp/venv/bin/activate
pip install build
python -m build            # creates dist/mazegen-1.0.0-py3-none-any.whl
cp dist/mazegen-1.0.0-py3-none-any.whl .
pip install ./mazegen-1.0.0-py3-none-any.whl
python -c "from mazegen import MazeGenerator; print(MazeGenerator)"
```

Add `from .cell import Cell` style imports to your files, and keep the `a_maze_ing.py` imports as `from mazegen import MazeGenerator`.

## 10.9 README checklist

- First line (italic): `*This activity has been created as part of the 42 curriculum by <login1>[, <login2>...]*`
- Sections: **Description**, **Instructions**, **Resources** (including how AI was used).
- Also: config file format, algorithm chosen **and why**, what is reusable and how, team/project management, bonus features.
- A short usage example of `MazeGenerator` (instantiate, custom size/seed, access the grid and a solution).

Whatever tool helped you, **make sure you can explain every line** in peer review.

## 10.10 Common mistakes (and the concept behind each)

| Mistake | Concept |
|---|---|
| Wall open on one side only | Use `link()` / `unlink()` (bidirectional) and never edit `_links` directly |
| Seeded maze different on each run | Iterating a `set` of cells, or using global `random` |
| `x`/`y` swapped | `(x, y) = (column, row)`; convert once |
| Entry or exit inside the 42 | Validate and raise a clear error |
| Binary Tree + 42 mask | Algorithm does not support masks (`supports_mask`) |
| 3×3 open block in non-perfect mode | Braiding guard (`has_open_block`) |
| Forgot the empty line in the output | File format step 2 |
| Crash with a traceback on bad config | `ConfigError` + `try/except` in `main` |
| Recursion error on big mazes | Use an explicit stack |

---

# Part 11: Appendices

## 11.1 Cheat sheet of all algorithms

| Algorithm | Kind | Bias / texture | Dead ends | Memory | Masks |
|---|---|---|---|---|---|
| Binary Tree | simple local | diagonal; two unbroken corridors | ~25% | none | no |
| Sidewinder | simple local | vertical; one unbroken corridor | ~27% | one row | no |
| Aldous-Broder | random walk | **none** | ~28-30% | none | yes |
| Wilson's | random walk | **none** | ~28-30% | list of unvisited | yes |
| Hunt-and-Kill | constrained walk | long twisty "river" | ~10% | none | yes |
| Recursive Backtracker | constrained walk | longest paths, "river" | ~10% | stack | yes |
| Kruskal's | set merging | nearly none, uniform | slightly above 30% | sets | yes |
| Simplified Prim's | frontier | radial burst | many | active list | yes |
| True Prim's | frontier | jigsaw look | most (about 45%) | active list + costs | yes |
| Growing Tree | frontier | depends on the selector | depends | active list | yes |
| Eller's | row sets | mild vertical bias | ~30% | one row | no |
| Recursive Division | wall adder | boxy, bottlenecks | many | recursion | no |

(Percentages are from the book's experiments: 1000 runs on a 32×32 grid, and 100 runs on 20×20 for the first chapters. Treat them as rough guides.)

Other measurements from the book:

- **Longest path:** Recursive Backtracker is the champion (about 50% of all cells on the longest path). Simplified Prim's has the shortest (under 10%).
- **Twistiness** (turns): Hunt-and-Kill, then Backtracker. True Prim's turns least.
- **Intersections:** Backtracker and Hunt-and-Kill have far fewer 3-way and 4-way crossings. Binary Tree has no 4-way crossings at all.

## 11.2 Glossary

| Word | Meaning |
|---|---|
| Algorithm | A step-by-step recipe |
| Bias | An algorithm's tendency to favour some mazes |
| Texture | The visual style of a maze |
| Cell | One square of the grid |
| Link | A passage (removed wall) between two cells |
| Neighbour | A cell adjacent in the grid |
| Perfect maze | One path between any two cells (a spanning tree) |
| Braid maze | Loops, few or no dead ends |
| Dead end | A cell with a single passage |
| Spanning tree | Loop-free graph touching every node |
| Frontier / active list | The cells currently being expanded |
| Run | Sidewinder's group of linked cells in a row |
| Set | Group of cells already connected (Kruskal's, Eller's) |
| Stack | LIFO list |
| Queue | FIFO list |
| BFS | Breadth-first search (flood fill) |
| DFS | Depth-first search (Recursive Backtracker) |
| Dijkstra | Cheapest path from one cell to all others |
| Weight | Cost of passing through a cell or passage |
| Mask | On/off map of usable cells |
| Inset | Gap that gives walls thickness |
| Weave | Passages crossing over/under each other |
| PRNG / seed | Pseudo-random generator / its starting value |
| Bitmask | Several flags stored in one integer |

## 11.3 Practice roadmap (in order)

1. Draw by hand a 4×4 maze with Binary Tree using a coin. Then with Sidewinder.
2. Build `Cell` and `Grid`; print a maze; change the grid size.
3. Make Binary Tree produce corridors on the south and west instead.
4. Implement Recursive Backtracker; count dead ends over 100 runs for three algorithms (the book's dead-end experiment).
5. Add BFS distances and print them in the cells; find the longest path.
6. Add a mask from a text drawing; then the "42" pattern.
7. Add `braid()`; color a braided maze; compare with the perfect one.
8. Write the config parser and the hex output; validate with the checker.
9. Add a second algorithm (Wilson's or Growing Tree) and select it via `ALGORITHM=` in the config.
10. Package everything as `mazegen`; rebuild in a clean virtual environment.
11. Bonus: Kruskal's with pre-placed crossings; hex or polar grid; infinite Eller's; a PNG renderer.

## 11.4 Testing ideas (even if tests are not graded)

```python
# snippet
def test_perfect_for_every_algorithm():
    for name in ALGORITHMS:
        grid = Grid(12, 12, seed=1)
        make_algorithm(name).generate(grid)
        assert is_perfect(grid)


def test_same_seed_same_maze():
    first = Grid(10, 10, seed=5)
    second = Grid(10, 10, seed=5)
    RecursiveBacktracker().generate(first)
    RecursiveBacktracker().generate(second)
    assert str(first) == str(second)
```

---

*End of the guide. Build it in small steps, run it often, and print the maze after every change.*
