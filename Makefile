
lint:
	ruff format toradh
	ruff format tests
	ruff format examples

check-style:
	ruff check