all: install lint test

lint:
	uvx ruff check .
	uvx ruff format .
	uvx ruff format --check .
	uv run pyright .

test: install
	uv run pytest

test-dev: install
	uv run pytest -vv -s

install:
	uv sync

run-dev:
	uv run granian --reload --interface asgi resentry.main:app
