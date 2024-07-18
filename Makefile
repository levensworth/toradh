
lint:
	poetry run ruff format toradh
	poetry run ruff format tests
	poetry run ruff format examples

check-style:
	poetry run ruff check

run_types:
	poetry run mypy toradh
	poetry run mypy tests

test:
	poetry run pytest --cov=toradh --cov-report=xml tests 