# A-Maze-ing — Full Solo Master Plan (Python, pure terminal UI, zero third-party libraries, 20 days)

Everything in one place: what to learn, the full folder structure, the design of every
module, and a day-by-day 20-day solo timeline. No code — pseudocode, signatures, and
worked-by-hand examples, so you design it before you type it.

**Change from the original plan:** the GUI is gone. There is no pygame, no pydantic, no
pip-installed dependency of any kind, anywhere in the repo — not even for `mazegen`, not
even for the display layer. Everything runs with `python3` and the standard library only
(`argparse`, `dataclasses`, `random`, `enum`, `abc`, `os`, `sys`, `typing`, `unittest` or
`pytest` if your grading rules require it — check whether `pytest` itself counts as an
allowed dev-only dependency, since that's the one exception worth confirming with your
subject/grader). The maze is drawn as text in the terminal, and interaction happens
through single-key or line commands read from stdin, not mouse clicks.

---

## 1. What you're building, in one paragraph

A CLI tool (`a_maze_ing.py config.txt`) that reads a config file, generates a maze (a
spanning tree over a grid = "perfect" maze, via a graph algorithm), writes it to a file as
hex-encoded wall bitmasks + entry/exit + shortest path, and then drops you into an
**interactive terminal session** — plain text redrawn in place — where single-key commands
let you regenerate the maze, toggle the solution path on/off, and cycle through a couple of
character/color themes (ANSI escape codes only, still zero libraries; degrades cleanly to
plain characters if the terminal doesn't support ANSI). Separately, the generation logic
must also exist as a standalone, pip-installable package (`mazegen-*.whl`) that someone
else could import and reuse — and that package stays import-clean with nothing but the
standard library, so anyone can `pip install` it without pulling in a dependency tree.

---

## 2. Concepts to understand before coding

| Concept | Why | Resource |
|---|---|---|
| Grid graph = maze | cells = nodes, open walls = edges | [Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html) |
| Spanning tree ⇔ perfect maze | why PERFECT=True means exactly one path | search "spanning tree" on Wikipedia |
| Recursive backtracker (DFS) | your chosen algorithm — simple, seedable | [Jamis Buck — Recursive Backtracker](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking) |
| BFS shortest path | solving the maze, used twice (output file + toggle-path command) | any "BFS grid maze solver" tutorial |
| Bitmask encoding | the hex wall format | re-read subject chapter 4.5 carefully |
| ABC / inheritance | `MazeAlgorithm` base class | Python `abc` module docs |
| `dataclasses` + manual validation | config file validation without pydantic | [Python `dataclasses` docs](https://docs.python.org/3/library/dataclasses.html) |
| mypy strict typing | required by grading rules | [mypy — getting started](https://mypy.readthedocs.io/en/stable/getting_started.html) |
| Terminal I/O basics | redrawing text in place, reading single keys | `os.system("clear")` / ANSI `\033[2J\033[H`; stdlib `tty`+`termios` (POSIX) or `msvcrt` (Windows) for single-keypress reads without Enter |
| ANSI escape codes | optional color, no library needed | search "ANSI escape codes color terminal" |
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
├── pyproject.toml                # packaging metadata for mazegen (no dependencies listed)
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
│   ├── config.py                 # ConfigModel (plain dataclass) + load_config()
│   ├── writer.py                 # write_output_file(maze, path)
│   └── errors.py                 # AMazeIngError hierarchy
│
├── terminal_ui/                  # text-only interactive session, stdlib only
│   ├── __init__.py
│   ├── session.py                # main input loop + AppState (replaces app.py)
│   ├── layout.py                 # pure math: terminal columns/rows needed, does it fit
│   ├── ascii_renderer.py         # draws walls, entry/exit, path, "42" highlight as text
│   ├── keymap.py                 # Command dataclass + key -> action lookup (replaces button.py)
│   └── theme.py                  # character sets + optional ANSI color codes + rotation
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
│   └── test_layout.py            # rendered maze fits inside a given terminal size, no crash
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
Unchanged from the GUI version — this module never touched pygame anyway.

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
output file's path line and the terminal session's "toggle path" command.

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
This class still has zero pygame or pydantic in it — that was already true in the GUI
version, so nothing here changes.

### 4.8 `io_utils/config.py` — no pydantic, plain dataclass + manual checks
```
@dataclass
class ConfigModel:
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool = True
    SEED: int | None = None

def load_config(path: str) -> ConfigModel:
    raw = _parse_key_value_lines(path)   # skip blank/# lines, split on first '='
    _require_keys(raw, {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE"})
    width = _parse_positive_int(raw["WIDTH"])
    height = _parse_positive_int(raw["HEIGHT"])
    entry = _parse_coord(raw["ENTRY"])
    exit_ = _parse_coord(raw["EXIT"])
    _require_in_bounds(entry, width, height)
    _require_in_bounds(exit_, width, height)
    _require_distinct(entry, exit_)
    perfect = _parse_bool(raw.get("PERFECT", "True"))
    seed = _parse_optional_int(raw.get("SEED"))
    return ConfigModel(width, height, entry, exit_, raw["OUTPUT_FILE"], perfect, seed)
```
Every `_parse_*` / `_require_*` helper raises a plain `ValueError` internally; `load_config`
catches those in one place and re-raises as your own `ConfigError` (see 4.10), so the
external behavior — "one error type at the boundary" — is identical to the pydantic version.
Write each helper as a small pure function so `test_config.py` can hit them individually,
not just through the full file-parsing path.

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

## 5. Terminal UI (pure text, single-key commands, no library)

`terminal_ui/` is a dependency of `a_maze_ing.py` only — `mazegen` never imports it, and
`terminal_ui` never imports anything outside the standard library. If you want smoother
single-keypress input (no Enter needed) you're allowed to reach for `tty`/`termios` on
POSIX or `msvcrt` on Windows — both are stdlib, not third-party — but a simpler and fully
portable fallback is `input()` reading one line per command (e.g. type `r` + Enter to
regenerate). Design for the `input()` version first; treat raw single-key capture as an
optional upgrade once everything else works, since it's the one part of this project with
real platform differences.

### 5.1 `keymap.py`
```
@dataclass
class Command:
    key: str
    label: str
    action: Callable[[], None]

def build_commands(state: AppState) -> list[Command]:
    return [
        Command("r", "regenerate", lambda: state.regenerate()),
        Command("p", "toggle path", lambda: state.toggle_path()),
        Command("t", "next theme", lambda: state.next_theme()),
        Command("q", "quit", lambda: state.request_quit()),
    ]
```
Same shape as the old `Button` list — a small dataclass plus a closure that mutates
`AppState` — just keyed by a typed character instead of a clicked rect. The 4 required
actions map 1:1 onto the 4 required buttons from the original plan.

### 5.2 `session.py` — main loop
```
def run(generator: MazeGenerator) -> None:
    state = AppState(generator=generator, show_path=False, theme_index=0)
    commands = build_commands(state)
    while not state.quit_requested:
        _clear_screen()
        print(ascii_renderer.render(state))
        _print_command_bar(commands)
        raw = input("> ").strip().lower()
        for c in commands:
            if raw == c.key:
                c.action()
                break
        else:
            if raw:
                print(f"unknown command: {raw!r}")
    _clear_screen()
```
`_clear_screen()` is `os.system("cls" if os.name == "nt" else "clear")`, or the ANSI
sequence `print("\033[2J\033[H", end="")` if you'd rather not shell out. Either way it's
still zero third-party libraries. Renderer should only ever read from `AppState`, never
hold its own maze copy — identical rule to the pygame version, just applied to text output.

### 5.3 `layout.py` — design on paper first
- `content_width = width * 2 + 1`, `content_height = height + 1` (two terminal characters
  per maze cell horizontally reads better than one; tune this once you see real output)
- `fits(term_columns, term_lines) -> bool`: does the rendered maze plus the command bar fit
  in the current terminal size (`os.get_terminal_size()`, stdlib)
- If it doesn't fit, `session.py` should print a clear message and exit cleanly rather than
  producing garbled wrapped output — this is the terminal equivalent of "buttons don't
  overlap the maze rect" from the GUI plan.
- Unit-testable without a real terminal: pass fixed `(columns, lines)` tuples into `fits()`
  and assert the boolean, exactly like the old button/maze-rect overlap test.

### 5.4 `ascii_renderer.py` — draw order matters
1. Walls: build the text grid cell by cell — each cell occupies a 2×1 (or larger) block;
   draw a wall character (`─`, `│`, `+`, or plain `-`/`|` if you want to stay ASCII-only)
   per **closed** wall, and a space for an open one
2. "42" reserved cells that are `is_fully_closed()` — filled with a distinct character
   (e.g. `#`), or an ANSI background color if `theme.supports_color()` is true
3. Path cells (if `state.show_path`) — a distinct character (e.g. `.`) or color, from
   `generator.solution()`
4. Entry (`S`) / Exit (`E`) characters — placed last so they always win over path/wall
   characters at the same cell
5. Return one big string (or a `list[str]`, one per line) so `session.py` does exactly one
   `print()` per frame — printing line-by-line as you build the grid causes visible flicker
   on some terminals.

### 5.5 `theme.py`
```
@dataclass(frozen=True)
class Theme:
    wall_char: str
    open_char: str
    path_char: str
    entry_char: str
    exit_char: str
    ansi_prefix: str = ""   # "" if color is off, else e.g. "\033[36m"
    ansi_reset: str = "\033[0m"

THEMES: list[Theme] = [ ... ]   # at least 2, so "next theme" is meaningfully different

def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
```
Always check `supports_color()` before emitting any ANSI code, and always have a plain
no-color theme as one of the options — this is your fallback for pipes, redirected output,
CI logs, and terminals that don't understand escape codes.

---

## 6. Makefile targets (reasoning, not just syntax)

- `install` → `pip install -e .` (installs `mazegen` in editable mode; nothing else to
  install, since there is no `requirements.txt` — the whole project is stdlib-only)
- `run` → `python3 a_maze_ing.py config.txt`
- `debug` → `python3 -m pdb a_maze_ing.py config.txt`
- `lint` → exactly the flake8 + mypy command from the subject
- `lint-strict` → `flake8 .` + `mypy . --strict`
- `clean` → remove `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, build artifacts (don't
  delete the committed `.whl` at repo root)

No target changes from the GUI plan — the Makefile never referenced pygame or pydantic by
name, so this section is unaffected by the switch.

---

## 7. Test plan

| File | Asserts |
|---|---|
| `test_cell.py` | wall bit flips affect only the targeted bit |
| `test_grid.py` | `carve(a,b,EAST)` opens both `a`'s EAST and `b`'s WEST |
| `test_backtracker.py` | same seed → identical maze; full connectivity via flood-fill |
| `test_rules.py` | hand-built 3×3 open block fails width check; too-small grid returns False from `stamp_pattern` without crashing |
| `test_solver.py` | BFS path matches your hand-traced tiny-maze path |
| `test_config.py` | missing key / bad value / ENTRY==EXIT → `ConfigError`, using the plain-dataclass parser (no pydantic `ValidationError` to catch anymore — every case funnels through your own `_parse_*`/`_require_*` helpers); valid file → correct `ConfigModel` |
| `test_writer.py` | byte-for-byte match against your hand-worked hex example |
| `test_layout.py` | `fits(columns, lines)` returns the right boolean for known terminal sizes; rendered string has the expected number of lines for a known small maze; no exception when the terminal is "too small" |

---

## 8. Full 20-day solo timeline

**Day 1 — Subject + design decisions**
- Read the subject twice (content, then edge cases).
- Confirm: recursive backtracker algorithm, terminal-based interactive session, stdlib only
  end to end (double-check your subject actually allows a text UI instead of a graphical
  one — this is the one assumption in this whole plan worth verifying before you build on it).
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

**Day 11 — Config parsing (no pydantic)**
- `config.py` (plain dataclass + `_parse_*`/`_require_*` helpers), `errors.py`,
  `test_config.py`. Since you're hand-rolling validation instead of leaning on a library,
  budget extra time for edge cases pydantic would have caught for free: whitespace around
  `=`, duplicate keys, non-integer `WIDTH`/`HEIGHT`, malformed `ENTRY`/`EXIT` tuples.

**Day 12 — Output writer**
- `writer.py`, `test_writer.py` against your hand example. Run the provided validation
  script for the first time; fix format mismatches immediately.

**Day 13 — CLI wiring**
- `a_maze_ing.py`: argv → config → generator → writer, single top-level error handler.
  Manually trigger every documented error case.

**Day 14 — Terminal layout + static render**
- `terminal_ui/layout.py` + `test_layout.py`. `terminal_ui/ascii_renderer.py` drawing one
  static maze (walls, entry, exit) to a plain `print()` before any interaction exists.
  Check it against at least two real terminal sizes, including a narrow one.

**Day 15 — Commands + input loop**
- `terminal_ui/keymap.py`, `terminal_ui/session.py`, `terminal_ui/theme.py`. Wire all 4
  required actions (regenerate / toggle path / next theme / quit) to `AppState`. Try every
  command at least three times, including garbage input and empty Enter presses.

**Day 16 — Packaging**
- `pyproject.toml` with an empty/absent `dependencies` list, build in a fresh venv, install
  the wheel, confirm `from mazegen import MazeGenerator` actually imports with nothing else
  installed in that venv. Copy artifact to repo root.

**Day 17 — Makefile + lint/mypy cleanup**
- All targets written and working. One dedicated pass fixing every flake8/mypy error
  across the whole repo. `.gitignore` finalized.

**Day 18 — README.md**
- Italic first line + login, Description, Instructions, Resources (real links + honest
  AI-usage notes), config format table, algorithm + why, what's reusable and how, a note
  that the project has zero third-party dependencies on purpose, and a short "project
  management" section (your actual timeline vs. this plan, retro, tools).

**Day 19 — Break your own program**
- Every bad-config case; fresh-clone `make install/run/debug/clean`; try the terminal
  session in a genuinely small terminal window and in a non-interactive/piped context
  (make sure it fails gracefully rather than hanging on `input()`); re-run the validation
  script once more.

**Day 20 — Final rebuild + self-defense rehearsal**
- Fresh venv, rebuild `mazegen` from source, run end-to-end again. Explain your own code
  out loud, function by function. Anything you can't explain cleanly is today's real task.

---

## 9. If you fall behind, protect these first

1. **Days 3–9** (the engine) — everything else depends on it being correct, not fast.
2. **Days 19–20** (hardening + rebuild rehearsal) — this is literally what gets tested live.
Polish on the terminal session (Days 14–15) is the safest thing to trim if time runs
short — a plain `print()` of one static maze beats a half-finished interactive loop with
broken commands.
