# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [0.0.6] - 2022-09-28

### Added

- `bind_mounts.py` script added to repository, but not added as an entrypoint. Meant only for synology.

### Fixed

- `mmm` no longer prints an invalid log message of unknown format when a known
  format is simply not provided in actions.

## [0.0.5] - 2022-09-27

### Added

- `filename_time_parse`: New utility to rename annoyingly time formatted files.

## [0.0.4] - 2022-09-27

### Added

- `mmm`: Now number of parallel copies/moves is configurable

## [0.0.3] - 2022-09-27

### Fixed

- Fix script entry point. Better usage description.

## [0.0.2] - 2022-09-26

### Added

- `mmm`: MultiMedia Move

## [0.0.1] - 2022-09-26

- initial release: Provides `split_manifest`

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[0.0.6]: https://github.com/sandipb/everyday-scripts/compare/v0.0.5..v0.0.6
[0.0.5]: https://github.com/sandipb/everyday-scripts/compare/v0.0.4..v0.0.5
[0.0.4]: https://github.com/sandipb/everyday-scripts/compare/v0.0.3..v0.0.4
[0.0.3]: https://github.com/sandipb/everyday-scripts/compare/v0.0.2..v0.0.3
[0.0.2]: https://github.com/sandipb/everyday-scripts/compare/v0.0.1..v0.0.2
[0.0.1]: https://github.com/sandipb/everyday-scripts/releases/tag/v0.0.1
