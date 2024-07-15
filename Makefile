
lint:
	poetry run ruff format toradh
	poetry run ruff format tests
	poetry run ruff format examples

check-style:
	poetry run ruff check