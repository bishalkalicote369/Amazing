
install:

run:
	@python3 a_maze_ing.py config.txt

debug:

clean:
	@rm -rf io_utils/__pycache__  mazegen/__pycache__

lint:
	@flake8 . and mypy . --warn-return-any --warn-unused-ignores
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 . && mypy --strict .
