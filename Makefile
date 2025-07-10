.PHONY: check mypy test fmt fmtdiff export ruffcheck rufffmt staticcheck install_hooks

check: staticcheck

ruffcheck:
	uv run ruff check everyday_scripts

# will fail if there are any diffs
rufffmt:
	uv run ruff format --diff everyday_scripts

staticcheck:
	uv run pyright everyday_scripts

fmt: rufffmt

test:
	uv run pytest

export: requirements.txt

requirements.txt: uv.lock
	uv export --no-hashes > $@

install_hooks:
	pre-commit install