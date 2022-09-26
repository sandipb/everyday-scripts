.PHONY: check mypy test fmt fmtdiff

check: mypy test

mypy:
	poetry run mypy everyday_scripts

fmtdiff:
	poetry run black --diff everyday_scripts

fmt:
	poetry run black everyday_scripts

test:
	poetry run pytest