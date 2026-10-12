ENV_NAME = .maze_env
VENV_PYTHON = $(ENV_NAME)/bin/python

install:
	@python -m venv $(ENV_NAME)


run:
	$(VENV_PYTHON) a_maze_ing.py config.txt

clean:
	@rm -rf io_utils/__pycache__  mazegen/__pycache__ mazegen/.mypy_cache \
	__pycache__ $(ENV_NAME) .mypy_cache

lint:
	@flake8 . && mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 . && mypy --strict .
