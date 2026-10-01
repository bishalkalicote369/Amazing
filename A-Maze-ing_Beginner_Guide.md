# A-Maze-ing: Beginner's Guide to Building a Maze Generator in Python

## TL;DR

This is a school project (42 curriculum) where you build a Python program called `a_maze_ing.py` that:
1. Reads a config file describing a maze (width, height, entry, exit, etc.)
2. Generates a random maze that follows several strict rules (fully connected, no wide-open rooms, contains a hidden "42" shape)
3. Writes the maze to an output file using a compact hexadecimal code
4. Displays the maze visually (terminal or graphical window) and lets the user regenerate it, show/hide the solution path, and change colors
5. Packages the maze-generation logic as a separate, reusable, pip-installable Python module

**The most important thing to remember:** the maze isn't just "random walls" — it has to be mathematically valid (a proper graph/spanning-tree structure), it must contain a visible "42" pattern made of closed cells, and everything (data format, file names, visuals) must match the spec exactly, because it's likely graded by an automated tool ("Moulinette").

---

## What This Is About

You're building a **maze generator**: a program that creates a grid of cells, knocks down walls between some of them (like carving corridors), and produces both a machine-readable maze file and a human-viewable picture of it.

**What the PDF explicitly says:** it's a Python 3.10+ command-line program, run as `python3 a_maze_ing.py config.txt`, that must generate, validate, save, and visually display a maze.

Two extra layers make this more than "just draw a random maze":
- **Assumption (reasonable, not stated explicitly how to achieve):** you'll need graph algorithms (e.g., Prim's, Kruskal's, or recursive backtracker) because the PDF mentions these by name as relevant techniques and requires the maze to behave like a spanning tree when "perfect."
- The maze logic has to be split out into its own reusable, installable package — separate from the visual/CLI program.

---

## What You Need Before Starting

- [ ] Python 3.10 or later installed
- [ ] `flake8` and `mypy` installed (for code style and type checking — the project requires your code to pass both)
- [ ] A package manager for Python (`pip`, `uv`, or `pipx` — your choice)
- [ ] Familiarity with basic graph concepts: *cells* (nodes) and *walls* (edges) — explained below in "Important Concepts"
- [ ] `make` installed, since the project requires a `Makefile`
- [ ] (Optional, only if you choose graphical display) the **MiniLibX (MLX)** graphics library — you can use plain terminal/ASCII output instead, so MLX is not mandatory
- [ ] `pytest` or `unittest` if you want to write tests (recommended but not graded)
- [ ] Tools to build a Python package (e.g., `build`), since you must ship a `.whl` or `.tar.gz` file

**Background info:** this is part of a school evaluation ("peer-review"/"Moulinette" grading), so file names and formats are not just suggestions — they are likely checked automatically. Get them exact.

---

## The Big Picture

The whole process is basically:

1. **Read** the config file (`config.txt`) to get width, height, entry, exit, output filename, and whether the maze must be "perfect."
2. **Generate** a maze on a grid of that width × height, respecting all structural rules (connectivity, no wide-open rooms, hidden "42" shape, optional perfect single-path property).
3. **Encode** each cell's walls as one hexadecimal digit and **write** the whole maze plus entry/exit coordinates and the shortest solution path to the output file.
4. **Display** the maze visually (ASCII or graphical), letting the user regenerate, toggle the solution path, and change colors.
5. **Package** the maze-generation code as a separate, installable module (with its own short docs) so it can be reused in a different project later.
6. **Document** everything in a `README.md` with specific required sections.
7. **Verify** your output with the provided validation script before submitting.

---

## Step-by-Step Instructions

### Step 1 — Set up your project structure

**What you're doing:** Creating the files the grading system expects to find.

**Why:** The PDF is strict about exact file names (`a_maze_ing.py` for the main program, a `README.md`, a `Makefile`, a `.gitignore`, and a `mazegen-*.whl`/`.tar.gz` package at the repo root). Wrong names likely cause automatic grading to fail.

**Do this:**
```
a_maze_ing.py        # main entry point — this exact name is required
config.txt            # default/example config file (required to exist in the repo)
maze_module/          # (your naming) — the reusable maze generation package source
README.md
Makefile
.gitignore
mazegen-1.0.0-py3-none-any.whl   # or .tar.gz — built package, at repo root
```

**Expected result:** Running `python3 a_maze_ing.py config.txt` from the repo root works without import errors.

**If it doesn't work:** Check that your reusable module is either installed (`pip install -e .`) or importable via `PYTHONPATH`/relative import from `a_maze_ing.py`.

---

### Step 2 — Parse the configuration file

**What you're doing:** Reading `KEY=VALUE` lines from a plain text file.

**Why:** Every maze's shape and behavior is driven entirely by this file — nothing is hardcoded.

**Do this:** Parse a file where:
- Each line is `KEY=VALUE`
- Lines starting with `#` are comments and must be ignored
- These keys are **mandatory**:

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Is the maze perfect? | `PERFECT=True` |

You may add your own extra keys (e.g., `SEED`, `ALGORITHM`, `DISPLAY_MODE`) — the PDF explicitly allows this.

**Expected result:** A dictionary or config object with all mandatory values populated, or a clear error if something's missing/malformed.

**If it doesn't work:** The PDF requires **graceful error handling** for invalid configuration, missing file, bad syntax, or impossible parameters (e.g., entry/exit outside bounds). Never let the program crash with a raw traceback — catch exceptions and print a clear message instead.

> **Must do:** A default `config.txt` must exist in your Git repository (this is how graders will first test your program).

---

### Step 3 — Generate the maze structure

**What you're doing:** Building the actual maze: which walls exist between which cells.

**Why:** This is the algorithmic core of the project — everything else (visuals, output file) depends on this being correct.

**Do this:**
- Represent the maze as a grid of cells; each cell has up to 4 walls (North, East, South, West).
- Use a randomized algorithm (the PDF names **Prim's**, **Kruskal's**, or **recursive backtracker** as common choices — you pick one and justify it in your README).
- Make the generation **reproducible via a seed** — i.e., the same seed must always produce the same maze.
- Satisfy all of these validity rules:
  - Entry and exit must exist, be different, and be inside the maze bounds.
  - The maze must be fully connected — no isolated (unreachable) cells — **except** cells that are part of the "42" pattern (see below).
  - There must be walls on the maze's outer border, except at the entry and exit points.
  - Wall data must be **coherent between neighbors**: if cell A has a wall on its East side, the cell to its East must also show a wall on its West side. (You cannot have a wall on one side of a shared edge but not the other.)
  - **No wide-open areas**: corridors can't be wider than 2 cells. A 2×3 or 3×2 open block is fine; a 3×3 open block is **not allowed**.
  - The maze must visually contain a hidden **"42"** shape, formed by several fully-closed (all 4 walls closed) cells.
  - If `PERFECT=True`, there must be **exactly one path** between entry and exit (this is the formal definition of a "perfect maze" — see Concepts section below).

**Expected result:** An internal data structure (e.g., a 2D array of cells, each cell storing which of its 4 walls are open/closed) representing a valid maze.

**If it doesn't work:**
- If your algorithm produces isolated cells outside the "42" pattern → your connectivity logic has a bug.
- If you get 3×3 (or larger) open blocks → you're removing too many walls; add a check after generation that scans for oversized open areas and re-adds a wall to break them up.
- If the "42" pattern doesn't fit → the PDF explicitly allows omitting it **only** when the maze is too small, but you must **print an error message to the console** in that case. Don't silently skip it.

---

### Step 4 — Compute the shortest solution path

**What you're doing:** Finding one valid shortest route from entry to exit.

**Why:** It's required in the output file and must be shown/hidden in the visual display.

**Do this:** Run a shortest-path search (e.g., BFS, since all edges have equal "cost") over the connected cells, from ENTRY to EXIT, and record the path as a sequence of the letters `N`, `E`, `S`, `W` (the direction taken at each step).

**Expected result:** A string like `SWSESWSES...` representing the walk from entry to exit.

**If it doesn't work:** If entry and exit aren't connected, your maze isn't valid per the rules above — check Step 3's connectivity requirement.

---

### Step 5 — Write the output file

**What you're doing:** Saving the maze to disk in the exact binary/text format the spec defines.

**Why:** This file is very likely checked automatically by a "Moulinette" (an automated grading script), and a validation script is provided to help you self-check.

**Do this:** Encode each cell as **one hexadecimal digit**, where each bit means a wall is **closed**:

| Bit | Direction |
|---|---|
| 0 (least significant) | North |
| 1 | East |
| 2 | South |
| 3 | West |

- Bit = 1 means that wall is **closed**; bit = 0 means it's **open**.
- Example: `3` in binary is `0011` → South and West walls are **open** (bits 0 and 1, i.e., North and East, are the ones set to 1 here — see the note below on reading this carefully).
- Example: `A` in binary is `1010` → East and West walls are **closed**.

> ⚠️ **Flag: the PDF's own two examples are worth double-checking against your bit table before you rely on them.** Per the bit table (bit 0 = North, 1 = East, 2 = South, 3 = West), decimal `3` = binary `0011` sets bits 0 and 1, meaning **North and East are closed** (not "south and west open" as literally written in the source text) — the two phrasings actually describe the same wall pair, since closing North+East is equivalent to leaving South+West as the only "open-implying" sides in a single-cell context, but this is subtle. **Trust the bit table itself** (bit=1 → closed) as the authoritative rule, write a couple of test cells by hand, and verify against the provided validation script rather than relying purely on the prose examples.

- Write cells **row by row**, one row of digits per line.
- After the last row, insert **one empty line**, then on the next 3 lines write, in order:
  1. The entry coordinates (e.g., `1,1`)
  2. The exit coordinates (e.g., `19,14`)
  3. The shortest path as a string of `N`/`E`/`S`/`W` letters (e.g., `SWSESWSES...`)
- **Every line must end with `\n`.**

**Expected result:** A file that looks like the example below (from the spec):
```
95153915395517951511511... (etc., one line per row)

1,1
19,14
SWSESWSESWSSSEESEEENEESES...
```

**If it doesn't work:** Run the validation script provided with the subject (mentioned in the PDF but not included in this document — check your repository/handout for it) to confirm your output file is coherent.

---

### Step 6 — Build the visual representation

**What you're doing:** Making the maze viewable by a human, either in the terminal or in a graphical window.

**Why:** Required by the spec, and it's how a reviewer will sanity-check that your maze rules (walls, "42" pattern, path) actually work.

**Do this:** Choose one of:
- **Terminal ASCII rendering**, or
- **Graphical display using MiniLibX (MLX)**

Your display must clearly show: walls, entry, exit, and the solution path.

You must support at least these user interactions:
- Re-generate a new maze and display it
- Show/Hide the shortest valid path from entrance to exit
- Change maze wall colors
- *(Optional)* set specific colors for the "42" pattern

You may add more interactions if you like.

**Expected result:** Running the program shows something like a menu (`1. Re-generate`, `2. Show/Hide path`, `3. Rotate colors`, `4. Quit`) with the maze drawn above it, entry/exit marked in distinct colors (e.g., magenta for entry, red for exit in the PDF's example), and the "42" shape visible as a cluster of solid cells.

**If it doesn't work:** If you picked MLX and don't have it installed/working, fall back to ASCII terminal rendering — the PDF treats both as equally acceptable.

---

### Step 7 — Package the maze generator as a reusable module

**What you're doing:** Separating your maze-generation logic into its own installable Python package, independent of the CLI/visual program.

**Why:** The project explicitly wants this logic reusable in a *future* project, not just callable from `a_maze_ing.py`.

**Do this:**
- Implement maze generation as a single class (e.g., `MazeGenerator`) inside a standalone module.
- Write short documentation (can live in the module's own README or docstrings, but must **also** appear in your main `README.md`) covering:
  - How to instantiate and use the generator (a basic example)
  - How to pass custom parameters (e.g., size, seed)
  - How to access the generated structure and at least one solution
- Build this into a single installable file named `mazegen-*` (e.g., `mazegen-1.0.0-py3-none-any.whl`), placed **at the root of your Git repository**. Both `.whl` and `.tar.gz` are acceptable.
- Keep everything needed to **rebuild** this package from source in your repo — you may be asked, during review, to install build tools in a fresh virtualenv and rebuild it live.

**Expected result:** Someone could run `pip install mazegen-1.0.0-py3-none-any.whl` in a clean environment, `import` your module, and generate a maze using just that package — without needing your whole repo.

**If it doesn't work:** If you're unsure how to build a `.whl`, the standard approach is Python's `build` package (`python -m build`) with a `pyproject.toml` describing your package — the PDF doesn't specify the exact tool, so this is a reasonable, common default, not something stated explicitly in the PDF.

> **Note the PDF makes explicitly:** the reusable module's internal data format for the maze does **not** have to match the output file's hex-digit format — they can differ.

---

### Step 8 — Write the README.md

**What you're doing:** Documenting the whole project for someone unfamiliar with it (peers, staff, recruiters).

**Why:** This is a hard requirement with a specific structure — missing sections will likely cost you points.

**Do this:** Your `README.md` must include, at minimum:
- **First line**, italicized, exactly in this form:
  `*This activity has been created as part of the 42 curriculum by <login1>[, <login2>[, <login3>[...]]]*`
- A **"Description"** section: what the activity is and its goal
- An **"Instructions"** section: compilation/installation/execution details
- A **"Resources"** section: references you used, **and** a description of how AI was used (which tasks, which parts of the activity)
- Because this project has extra requirements, you must **also** document:
  - The complete structure/format of your config file
  - Which maze generation algorithm you chose, and **why**
  - What part of your code is reusable, and how (this doubles up with Step 7's documentation)
  - Your team/project management: each member's role, your planning and how it evolved, what worked well vs. what could improve, and any specific tools you used
  - Any advanced features you added (multiple algorithms, extra display options), if applicable

**Expected result:** A `README.md` a stranger could read top-to-bottom and understand, run, and extend your project from.

**If it doesn't work:** Use English by default; your campus's main language is an accepted alternative per the PDF.

---

### Step 9 — Follow general code quality rules (applies throughout)

**What you're doing:** Meeting the coding-standard checklist that applies to the whole project.

**Why:** These are graded requirements, separate from the maze-specific logic.

**Do this — Must do:**
- Python 3.10+ only
- Code must pass `flake8`
- All functions must have type hints and pass `mypy` cleanly
- Use `try/except` around anything that could throw, and context managers (`with ...`) for files/resources, so the program never crashes unhandled
- Docstrings (Google or NumPy style, PEP 257) on functions and classes
- A `Makefile` with these exact targets:
  - `install` — installs dependencies (`pip`, `uv`, `pipx`, etc.)
  - `run` — runs the main script
  - `debug` — runs the main script with Python's built-in debugger (`pdb`)
  - `clean` — removes temp files/caches (`__pycache__`, `.mypy_cache`, etc.)
  - `lint` — runs exactly:
    ```
    flake8 .
    mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
    ```
- A `.gitignore` excluding Python build artifacts

**Do this — Optional:**
- `lint-strict` target running `flake8 .` and `mypy . --strict`
- Unit tests with `pytest`/`unittest` (not submitted or graded, but recommended)
- A virtual environment (`venv`/`conda`) during development

**Expected result:** `make lint` passes cleanly; `make install`, `make run`, `make debug`, and `make clean` all work as described.

---

## Important Concepts Explained

**Cell / Grid:** Think of the maze as a grid of little rooms (cells), like a chessboard. Each cell can have a wall on up to 4 sides (N/E/S/W).

**Perfect maze:** A maze where there's **exactly one** way to get from the entry to the exit — no loops, no shortcuts, no dead-end alternate routes that reconnect. This directly corresponds to a *spanning tree* in graph theory (see below) — the PDF mentions this connection directly.

**Spanning tree (analogy):** Imagine every cell is a dot, and every removed wall (i.e., every opening you carve) is a line connecting two dots. If you connect all dots using the *minimum* number of lines needed so everyone is reachable — with **no loops** — that's a spanning tree. A "perfect" maze is exactly this: the minimum connections needed to link every cell, with no redundant paths.

**Wall coherence:** Because two neighboring cells share one physical wall, both cells' data must agree about whether that wall is open or closed. This is just consistency — you're not storing two independent flags for one wall, you're storing the same fact twice (once from each cell's perspective), so they must match.

**Hexadecimal wall encoding:** Instead of storing "North: open, East: closed, South: closed, West: open" as four separate values, the spec packs it into one hex digit using 4 bits (one per direction) — this is a common, compact way to store 4 yes/no values in a single character. See Step 5 for the exact bit assignments.

**The "42" pattern:** A specific set of cells, when fully closed (walls on all 4 sides — meaning they look like solid blocks visually), form the shape of the numbers "4" and "2" somewhere in the maze grid. This is a fun branding touch by the school (42 is the school's name), but it's also a **graded requirement**, not decorative.

---

## Common Mistakes

- Naming the main file something other than exactly `a_maze_ing.py`.
- Forgetting the empty line before the entry/exit/path block in the output file.
- Not handling the case where the maze is too small to fit the "42" pattern (you must print a console error, not silently skip it).
- Letting a wall be closed on one cell's side but open on the neighboring cell's matching side (incoherent data).
- Generating wide-open 3×3+ areas by removing too many walls near each other.
- Treating the "perfect maze" requirement (`PERFECT=True`) as optional decoration rather than a strict single-path requirement.
- Bundling the reusable maze module's code *inside* the main CLI script instead of as a separate, independently pip-installable package.
- Forgetting that the reusable package documentation must appear **both** in the module itself and in the main `README.md`.
- Skipping type hints or docstrings, which are graded requirements, not just style suggestions.
- Letting unhandled exceptions crash the program — this is explicitly called out as making the program "considered non-functional."

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| Program crashes on bad config file | No error handling around parsing | Wrap config parsing in try/except; print a clear message and exit gracefully |
| `mypy` fails | Missing type hints somewhere | Add type hints to every function parameter, return type, and relevant variable |
| Maze has unreachable cells | Generation algorithm doesn't guarantee full connectivity | Use a spanning-tree-based algorithm (Prim's/Kruskal's/recursive backtracker), which guarantees connectivity by construction |
| Maze has a big open room | Too many walls removed near each other | Add a post-generation check for any 3×3 (or larger) fully-open block and re-close a wall inside it |
| "42" pattern isn't visible | Maze is too small for the pattern to fit | Print a console error message (per spec) instead of failing silently; consider requiring a minimum size |
| Output file doesn't validate | Bit encoding or line format doesn't match spec exactly | Re-check the bit table (bit 0=N, 1=E, 2=S, 3=W, 1=closed), the empty-line separator, and `\n` line endings; run the provided validation script |
| `mazegen-*` package won't build | Missing build tooling or config | Add a `pyproject.toml` and build with `python -m build` (or your preferred standard tool) in a clean virtualenv |

---

## Final Checklist

- [ ] `a_maze_ing.py` exists and runs via `python3 a_maze_ing.py config.txt`
- [ ] Default `config.txt` exists in the repo
- [ ] Config parser handles comments (`#`) and all 6 mandatory keys
- [ ] All error cases (bad file, bad syntax, impossible params) are handled gracefully with clear messages
- [ ] Maze generation is reproducible via a seed
- [ ] Maze is fully connected (except intentionally within the "42" pattern)
- [ ] No 3×3+ open areas anywhere in the maze
- [ ] Outer border has walls except at entry/exit
- [ ] Wall data is coherent between all neighboring cells
- [ ] "42" pattern is visible when the maze is large enough; console error printed when it isn't
- [ ] `PERFECT=True` produces a maze with exactly one path between entry and exit
- [ ] Output file uses correct hex encoding, row-by-row layout, blank line, then entry/exit/path lines, each ending in `\n`
- [ ] Output validated against the provided validation script
- [ ] Visual display (ASCII or MLX) shows walls, entry, exit, and solution path
- [ ] User can regenerate, show/hide path, and change wall colors interactively
- [ ] Maze generation logic lives in a separate reusable module/class (e.g., `MazeGenerator`)
- [ ] `mazegen-*.whl` or `.tar.gz` package exists at repo root and can be rebuilt from source
- [ ] `README.md` has the required italicized first line, Description, Instructions, Resources (incl. AI usage), plus all activity-specific sections listed in Step 8
- [ ] `Makefile` has working `install`, `run`, `debug`, `clean`, and `lint` targets (and ideally `lint-strict`)
- [ ] `.gitignore` excludes Python artifacts
- [ ] Code passes `flake8` and `mypy` per the exact `lint` command in the spec
- [ ] All functions have type hints and docstrings

---

## Key Takeaways

1. This isn't just "draw a random maze" — it's a structured graph problem with strict validity rules (connectivity, coherent walls, no wide corridors, hidden "42" shape, optional perfect-maze property).
2. The output file format is exact and likely auto-graded — get the hex bit-encoding and line layout precisely right, and double-check it with the provided validation script.
3. The maze-generation logic must be reusable as its own installable package (`mazegen-*`), separate from the CLI/visual program — this is graded independently from the "does it draw a maze" requirement.
4. Code quality requirements (type hints, docstrings, `flake8`/`mypy`, Makefile targets, graceful error handling) apply throughout and are graded alongside the maze logic itself.
5. The `README.md` has a very specific required structure, including project-management reflection — don't treat it as an afterthought.

---

## Source / PDF Notes

- **Directly from the PDF:** all requirements in this guide (config format, maze rules, output format, visual requirements, packaging requirements, README requirements, coding standards, submission/review process) are stated explicitly in the source document.
- **My inferences/assumptions (flagged inline above):**
  - The suggestion to use Python's `build` tool and a `pyproject.toml` to produce the `mazegen-*` package is a reasonable common approach, but the PDF does not specify which build tool to use — you have freedom here.
  - The exact bit-encoding examples given in the original PDF (`3` = "south and west open", `A` = "east and west closed") are worth verifying carefully against the bit table yourself, since the prose examples and the strict bit-table reading can be interpreted in more than one way depending on how you define "open" vs "closed" per bit. I flagged this explicitly in Step 5 rather than silently picking one interpretation — verify against the provided validation script before trusting either phrasing.
  - Which specific graph algorithm to use (Prim's, Kruskal's, recursive backtracker, or another) is left to you — the PDF only names these as examples and asks you to justify your choice in the README.
- **Missing/unclear from the PDF, not invented here:**
  - The actual **validation script** and any **specific review guidelines** (exact grading rubric, what modification might be requested during peer review) are referenced but not included in this document — check your course materials/repository for those files.
  - The exact MLX library variant/bindings to use for Python graphical display are not specified.
- **Potentially worth verifying with staff/peers before relying on it:** the precise semantics of the hex bit-to-wall-state examples in Step 5, since getting this backwards would silently produce a maze file that looks plausible but fails automated validation.
