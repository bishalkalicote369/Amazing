# A-Maze-ing — Full Solo Master Plan (Python + pygame GUI, 20 days)

Everything in one place: what to learn, the full folder structure, the design of every
module, and a day-by-day 20-day solo timeline. No code — pseudocode, signatures, and
worked-by-hand examples, so you design it before you type it.

---

## 1. What you're building, in one paragraph

A CLI tool (`a_maze_ing.py config.txt`) that reads a config file, generates a maze (a
spanning tree over a grid = "perfect" maze, via a graph algorithm), writes it to a file as
hex-encoded wall bitmasks + entry/exit + shortest path, and shows it in a **pygame window
with clickable buttons** (regenerate / show-hide path / change colors / optional 42-color).
Separately, the generation logic must also exist as a standalone, pip-installable package
(`mazegen-*.whl`) that someone else could import and reuse.

---

## 2. Concepts to understand before coding

| Concept | Why | Resource |
|---|---|---|
| Grid graph = maze | cells = nodes, open walls = edges | [Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html) |
| Spanning tree ⇔ perfect maze | why PERFECT=True means exactly one path | search "spanning tree" on Wikipedia |
| Recursive backtracker (DFS) | your chosen algorithm — simple, seedable | [Jamis Buck — Recursive Backtracker](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking) |
| BFS shortest path | solving the maze, used twice (output file + show/hide path) | any "BFS grid maze solver" tutorial |
| Bitmask encoding | the hex wall format | re-read subject chapter 4.5 carefully |
| ABC / inheritance | `MazeAlgorithm` base class | Python `abc` module docs |
| pydantic | config file validation | [pydantic — models](https://docs.pydantic.dev/latest/concepts/models/) |
| mypy strict typing | required by grading rules | [mypy — getting started](https://mypy.readthedocs.io/en/stable/getting_started.html) |
| pygame events/drawing | GUI + mouse buttons | [pygame docs](https://www.pygame.org/docs/), [event module](https://www.pygame.org/docs/ref/event.html), [draw module](https://www.pygame.org/docs/ref/draw.html), [`Rect.collidepoint`](https://www.pygame.org/docs/ref/rect.html#pygame.Rect.collidepoint) |
| Python packaging | building `mazegen-*.whl` | [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) |
| Makefile basics | required targets | [makefiletutorial.com](https://makefiletutorial.com/) |

---

## 3. Full repository tree

```
a-maze-ing/
├── a_maze_ing.py                 # CLI entry point
├── config.txt                    # default config, committed (mandatory)
├── config.small.txt              # tiny config for quick manual tests
├── config.no42.txt               # config too small for "42" pattern, tests that error path
├── Makefile
├── README.md
├── .gitignore
├── pyproject.toml                # packaging metadata for mazegen
├── mazegen-1.0.0-py3-none-any.whl  # final built package, lives at repo root
│
├── mazegen/                      # <-- becomes the pip package, dependency-free
│   ├── __init__.py               # re-exports MazeGenerator, Cell, Direction
│   ├── cell.py                   # Cell dataclass: walls bitmask, position
│   ├── grid.py                   # Grid: 2D array of Cells, neighbor lookup, carve()
│   ├── directions.py             # Direction enum (N,E,S,W), bit values, opposite(), delta()
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── base.py               # ABC MazeAlgorithm
│   │   └── backtracker.py        # RecursiveBacktracker(MazeAlgorithm)
│   ├── rules.py                  # corridor-width check, "42" pattern stamping
│   ├── solver.py                 # BFS shortest path
│   ├── generator.py              # MazeGenerator — public orchestrator class
│   └── py.typed
│
├── io_utils/
│   ├── __init__.py
│   ├── config.py                 # ConfigModel (pydantic) + load_config()
│   ├── writer.py                 # write_output_file(maze, path)
│   └── errors.py                 # AMazeIngError hierarchy
│
├── display/                      # pygame GUI, mouse-driven
│   ├── __init__.py
│   ├── app.py                    # window + main event loop + AppState
│   ├── layout.py                 # pure math: cell size, maze offset, button rects
│   ├── grid_renderer.py          # draws walls, entry/exit, path, "42" highlight
│   ├── button.py                 # Button dataclass + click hit-testing
│   └── colors.py                 # RGB palettes + rotation
│
├── tests/
│   ├── conftest.py
│   ├── test_cell.py
│   ├── test_grid.py
│   ├── test_backtracker.py
│   ├── test_rules.py
│   ├── test_solver.py
│   ├── test_config.py
│   ├── test_writer.py
│   └── test_layout.py            # button/maze rects don't overlap, cell size math
│
└── dist/                          # build output (gitignored except final artifact copied to root)
```

---

## 4. Module design

### 4.1 `directions.py`
```
class Direction(Enum):
    NORTH = 1; EAST = 2; SOUTH = 4; WEST = 8
    def opposite(self) -> "Direction": ...
    def delta(self) -> tuple[int, int]: ...
```
Centralize `opposite()` here — every wall you carve must open **both** sides (this cell's
wall and the neighbor's matching wall), and this is the one place that mapping should live.

### 4.2 `cell.py`
```
@dataclass
class Cell:
    x: int; y: int; walls: int = 0b1111   # start fully closed
    def has_wall(self, d: Direction) -> bool: ...
    def open_wall(self, d: Direction) -> None: ...
    def close_wall(self, d: Direction) -> None: ...
    def is_fully_closed(self) -> bool: ...
```

### 4.3 `grid.py`
```
class Grid:
    width: int; height: int; cells: list[list[Cell]]
    def in_bounds(self, x, y) -> bool: ...
    def neighbor(self, cell, d) -> Cell | None: ...
    def carve(self, a, b, d) -> None: ...   # opens a→d and b→opposite(d) together
    def all_cells(self) -> Iterator[Cell]: ...
```
Keep `Grid` "dumb": geometry + wall coherence only. It knows nothing about mazes being
perfect or about "42" — that's `rules.py`'s job. This separation is what makes it reusable.

### 4.4 `algorithms/base.py` + `backtracker.py`
```
class MazeAlgorithm(ABC):
    def __init__(self, grid: Grid, rng: random.Random) -> None: ...
    @abstractmethod
    def run(self, start: Cell) -> None: ...
```
Recursive backtracker, pseudocode:
```
stack = [start]; visited = {start}
while stack:
    current = stack[-1]
    unvisited = [n for n in neighbors(current) if n not in visited]
    if unvisited:
        nxt = rng.choice(unvisited)
        grid.carve(current, nxt, direction_to(current, nxt))
        visited.add(nxt); stack.append(nxt)
    else:
        stack.pop()
```
Use `random.Random(seed)`, never the global `random` module, or reproducibility breaks
silently the moment two mazes generate in one process.

### 4.5 `rules.py`
```
def has_no_wide_open_area(grid, max_size=2) -> bool: ...   # scan 3x3 windows
def stamp_pattern(grid, pattern="42") -> bool: ...          # reserve cells BEFORE generation
def is_perfect_maze(grid, entry, exit) -> bool: ...          # sanity check
```
Approach for "42": design a small bitmap of reserved cells, mark them "do not carve"
*before* running the algorithm, and make the algorithm skip reserved cells as neighbor
candidates. Don't try to detect the pattern after the fact — bake it in instead.

### 4.6 `solver.py`
```
def shortest_path(grid, entry, exit) -> list[Direction]: ...
```
Plain BFS over open walls, reconstructed via `came_from`. Write once, use for both the
output file's path line and the GUI's "show/hide path" button.

### 4.7 `generator.py` — the public pip-installable API
```
class MazeGenerator:
    def __init__(self, width, height, entry, exit, perfect=True, seed=None,
                 algorithm="backtracker") -> None: ...
    def generate(self) -> None: ...
        # stamp "42" reserved cells -> run algorithm -> if not perfect, remove a few
        # extra walls for loops -> validate rules
    @property
    def grid(self) -> Grid: ...
    def solution(self) -> list[Direction]: ...
    def to_hex_rows(self) -> list[str]: ...
```
Write its docstring like a tutorial now — it gets copied almost verbatim into README.md.

### 4.8 `io_utils/config.py`
```
class ConfigModel(BaseModel):
    WIDTH: int; HEIGHT: int
    ENTRY: tuple[int, int]; EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool = True
    SEED: int | None = None
    # validators: positive width/height, entry/exit in-bounds and distinct
```
Parse: read lines → skip blank/`#` → split on first `=` → dict → `ConfigModel(**raw)`.
Catch `ValidationError` once, at the top, convert to your own `ConfigError`.

### 4.9 `io_utils/writer.py` — worked hex example (redo this by hand yourself)

2×2 grid, entry (0,0), exit (1,1), one internal wall open east/west and one open north/south:
```
Cell(0,0): N=1 E=0 S=0 W=1 -> binary 1001 -> hex 9
Cell(1,0): N=1 E=1 S=1 W=0 -> binary 1110 -> hex E
Cell(0,1): N=0 E=1 S=1 W=1 -> binary 0111 -> hex 7
Cell(1,1): N=1 E=1 S=1 W=1 -> binary 1111 -> hex F
```
```
9E
7F

0,0
1,1
<path letters>
```
Redo this on your own tiny example until the hex digits match your own bit-order logic —
this catches an off-by-one before it's buried in code.

### 4.10 `io_utils/errors.py`
```
class AMazeIngError(Exception): ...
class ConfigError(AMazeIngError): ...
class MazeGenerationError(AMazeIngError): ...
class MazeIOError(AMazeIngError): ...
```
One `try/except AMazeIngError` in `main()` satisfies "never crash unexpectedly" in one place.

---

## 5. GUI (pygame, mouse buttons)

Keep pygame as a dependency of `display/` and `a_maze_ing.py` only — **not** of `mazegen`,
which stays dependency-free.

### 5.1 `button.py`
```
@dataclass
class Button:
    rect: pygame.Rect
    label: str
    action: Callable[[], None]
    def draw(self, surface, font) -> None: ...
    def is_clicked(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)
```
Build the 4 required buttons as `list[Button]`, each `action` a closure mutating `AppState`.

### 5.2 `app.py` — event loop
```
def run(generator: MazeGenerator) -> None:
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    state = AppState(generator=generator, show_path=False, palette_index=0)
    buttons = build_buttons(state)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.is_clicked(event.pos):
                        b.action(); break
        screen.fill(BG_COLOR)
        grid_renderer.draw(screen, state)
        for b in buttons: b.draw(screen, font)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
```
`event.button == 1` = left click only. Check buttons only on `MOUSEBUTTONDOWN`, not every
frame. Renderer should only ever read from `AppState`, never hold its own maze copy.

### 5.3 `layout.py` — design on paper first
- `cell_size = min(available_w // width, available_h // height)`
- `maze_origin` centers the maze, leaves room below for buttons
- `button_rects`: one row of 4 rects below the maze, computed once at startup
- Unit-testable: given a fixed window/maze size, assert no button rect overlaps the maze rect.

### 5.4 `grid_renderer.py` — draw order matters
1. Walls: for each cell, draw a line per **closed** wall (open = no line = passable)
2. "42" reserved cells that are `is_fully_closed()` — filled with a distinct color
3. Path cells (if `state.show_path`) — highlight color, from `generator.solution()`
4. Entry (green) / Exit (red) squares — drawn last so always visible

---

## 6. Makefile targets (reasoning, not just syntax)

- `install` → `pip install -e .` (or `pip install -r requirements.txt` if you add pygame there)
- `run` → `python3 a_maze_ing.py config.txt`
- `debug` → `python3 -m pdb a_maze_ing.py config.txt`
- `lint` → exactly the flake8 + mypy command from the subject
- `lint-strict` → `flake8 .` + `mypy . --strict`
- `clean` → remove `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, build artifacts (don't
  delete the committed `.whl` at repo root)

---

## 7. Test plan

| File | Asserts |
|---|---|
| `test_cell.py` | wall bit flips affect only the targeted bit |
| `test_grid.py` | `carve(a,b,EAST)` opens both `a`'s EAST and `b`'s WEST |
| `test_backtracker.py` | same seed → identical maze; full connectivity via flood-fill |
| `test_rules.py` | hand-built 3×3 open block fails width check; too-small grid returns False from `stamp_pattern` without crashing |
| `test_solver.py` | BFS path matches your hand-traced tiny-maze path |
| `test_config.py` | missing key / bad value / ENTRY==EXIT → `ConfigError`; valid file → correct model |
| `test_writer.py` | byte-for-byte match against your hand-worked hex example |
| `test_layout.py` | button rects and maze rect never overlap; cell_size math is correct for a known input |

---

## 8. Full 20-day solo timeline

**Day 1 — Subject + design decisions**
- Read the subject twice (content, then edge cases).
- Confirm: recursive backtracker algorithm, pygame GUI with buttons.
- Sketch the empty folder tree from section 3 into the repo (empty files, no logic).
- Lock down the `MazeGenerator` constructor/API on paper.

**Day 2 — Hand-worked examples**
- Hand-encode a tiny maze into hex (section 4.9). Hand-trace its BFS shortest path.
- Save both as your first test fixtures.

**Day 3 — Foundations**
- `directions.py`, `cell.py`. Quick manual sanity check of bit math.

**Day 4 — Grid + wall coherence**
- `grid.py`, `test_grid.py`. Don't move on until `carve()` is proven correct.

**Day 5 — Algorithm**
- `algorithms/base.py`, `backtracker.py`. Manual debug print of a generated maze.

**Day 6 — Test the algorithm**
- `test_backtracker.py`: reproducibility + connectivity.

**Day 7 — Solver**
- `solver.py`, `test_solver.py` against your Day 2 hand-traced path.

**Day 8 — Corridor-width rule**
- `rules.py::has_no_wide_open_area`, tested against a broken and a valid grid.

**Day 9 — "42" pattern (budget the full day)**
- Reserved-cell bitmap, algorithm skips reserved neighbors, too-small-maze graceful path.

**Day 10 — `MazeGenerator`**
- Tie everything together; write the tutorial-style docstring now.

**Day 11 — Config parsing**
- `config.py` (pydantic), `errors.py`, `test_config.py`.

**Day 12 — Output writer**
- `writer.py`, `test_writer.py` against your hand example. Run the provided validation
  script for the first time; fix format mismatches immediately.

**Day 13 — CLI wiring**
- `a_maze_ing.py`: argv → config → generator → writer, single top-level error handler.
  Manually trigger every documented error case.

**Day 14 — GUI layout + static render**
- `display/layout.py` + `test_layout.py`. `display/grid_renderer.py` drawing one static
  maze (walls, entry, exit) before any interaction exists.

**Day 15 — Buttons + event loop**
- `display/button.py`, `display/app.py`. Wire all 4 required actions to `AppState`.
  Click everything at least three times, including near-misses just outside buttons.

**Day 16 — Packaging**
- `pyproject.toml`, build in a fresh venv, install the wheel, confirm
  `from mazegen import MazeGenerator` actually imports. Copy artifact to repo root.

**Day 17 — Makefile + lint/mypy cleanup**
- All targets written and working. One dedicated pass fixing every flake8/mypy error
  across the whole repo. `.gitignore` finalized.

**Day 18 — README.md**
- Italic first line + login, Description, Instructions, Resources (real links + honest
  AI-usage notes), config format table, algorithm + why, what's reusable and how, and a
  short "project management" section (your actual timeline vs. this plan, retro, tools).

**Day 19 — Break your own program**
- Every bad-config case; fresh-clone `make install/run/debug/clean`; re-run the
  validation script once more.

**Day 20 — Final rebuild + self-defense rehearsal**
- Fresh venv, rebuild `mazegen` from source, run end-to-end again. Explain your own code
  out loud, function by function. Anything you can't explain cleanly is today's real task.

---

## 9. If you fall behind, protect these first

1. **Days 3–9** (the engine) — everything else depends on it being correct, not fast.
2. **Days 19–20** (hardening + rebuild rehearsal) — this is literally what gets tested live.
Polish on the GUI (Days 14–15) is the safest thing to trim if time runs short — a working
but plain window beats a broken fancy one.
