.PHONY: check mypy test fmt fmtdiff export ruffcheck rufffmt staticcheck install_hooks

check: staticcheck

ruffcheck:
	poetry run ruff check everyday_scripts

# will fail if there are any diffs
rufffmt:
	poetry run ruff format --diff everyday_scripts

staticcheck:
	poetry run pyright everyday_scripts

fmt: rufffmt

test:
	poetry run pytest

export: requirements.txt

requirements.txt: poetry.lock
	poetry export --without-hashes > $@

install_hooks:
	pre-commit install