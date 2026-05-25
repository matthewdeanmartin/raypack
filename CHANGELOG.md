# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Mark project as archived with explanation
- Fix transitive dependencies to reduce vulnerabilities (Snyk SNYK-PYTHON-RAY-14129882)
- Mypy handling for str and list instances

## [0.4.0] - 2023-11-03

### Changed
- Update pre-commit hooks and relax Poetry dependency constraints in pyproject.toml
- Improve `poetry_interface` to handle edge cases in virtual environment detection

## [0.3.20] - 2023-11-02

### Changed
- Refactor Poetry interface to fix virtual environment creation and dependency installation
- Remove dist-info entries from packaged zip to avoid conflicts in AWS Glue runtime

## [0.3.1] - 2023-10-29

### Added
- Add S3 upload capability

## [0.3.0] - 2023-10-29

### Changed
- Extract core packaging logic from `__main__.py` into a dedicated `build.py` module
- Add `logging_utils.py` for structured logging configuration
- Fix mypy errors for `str` and `list` type instance checks

## [0.2.23] - 2023-10-29

### Fixed
- Fix bug in `build.py` where S3 upload path was constructed incorrectly
- Add more logging output during package build steps

## [0.2.18] - 2023-10-27

### Changed
- Convert from Pipenv to Poetry

## [0.1.0] - 2023-01-01

### Added
- Reserve package name and establish initial project idea

[Unreleased]: https://github.com/matthewdeanmartin/raypack/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/matthewdeanmartin/raypack/compare/v0.3.20...v0.4.0
[0.3.20]: https://github.com/matthewdeanmartin/raypack/compare/v0.3.1...v0.3.20
[0.3.1]: https://github.com/matthewdeanmartin/raypack/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/matthewdeanmartin/raypack/compare/v0.2.23...v0.3.0
[0.2.23]: https://github.com/matthewdeanmartin/raypack/compare/v0.2.18...v0.2.23
[0.2.18]: https://github.com/matthewdeanmartin/raypack/compare/v0.1.0...v0.2.18
[0.1.0]: https://github.com/matthewdeanmartin/raypack/compare/v0.1.0...v0.1.0
