# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a collection of personal utility scripts for desktop and server administration.
The project is organized as a Python package with uv for dependency management and includes both Python
scripts and shell utilities.

## Development Commands

### Setup and Installation

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
make install_hooks
```

### Code Quality and Testing

```bash
# Run all static checks
make check

# Run type checking
make staticcheck
uv run pyright everyday_scripts

# Run linting
make ruffcheck
uv run ruff check everyday_scripts

# Check formatting (will fail if changes needed)
make rufffmt
uv run ruff format --diff everyday_scripts

# Run tests
make test
uv run pytest

# Export requirements.txt
make export
```

### Build System

- Uses uv for Python dependency management
- Bazel build system is also configured (requires `bazelisk` and `buildifier`)
- Pre-commit hooks are available for code quality enforcement

## Architecture

### Core Components

1. **scriptlib.py** - Shared library containing common utilities:
   - Colored console output functions (`msg_info`, `msg_error`)
   - Interactive prompts (`ask`)
   - Logging configuration with colored output
   - Signal handling for clean exits
   - Utility functions like `chunks` for list processing

2. **Individual Script Tools** - Each script is a standalone utility:
   - **mmm.py** - File mover based on MIME types with async processing
   - **imap_tools.py** - IMAP server operations toolkit using Click CLI
   - **bq_*.py** - BigQuery management utilities
   - **gh_list_changed.py** - GitHub API integration
   - **bcrypt_util.py** - Password hashing utilities

### Script Entry Points

Scripts are configured as console entry points in `pyproject.toml` under `[project.scripts]`.
They can be run directly after installation or via `uv run <script-name>`.

### Code Style Configuration

- **Line length**: 140 characters (configured in both Ruff and Black)
- **Python version**: 3.11+
- **Formatting**: Ruff with isort for import sorting
- **Type checking**: Pyright with strict configuration
- **Pre-commit hooks**: Available for automated code quality checks

### Common Patterns

- Scripts use the shared `scriptlib` module for consistent UX
- Click framework for CLI interfaces where multiple subcommands are needed
- Async operations use `trio` library
- Error handling with colored output and proper logging
- Type hints are used throughout

## Testing

- Tests are in the `tests/` directory
- Run tests with `uv run pytest` or `make test`
- Test files follow the pattern `test_*.py`
