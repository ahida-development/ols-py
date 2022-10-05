# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2022-10-05
### Changed
- Added documentation for schema fields

## [0.2.1] - 2022-10-05
### Changed
- Reworked documentation

## [0.2.0] - 2022-10-05
### Changed
- Refactored schemas to better separate schemas used in requests from schemas for responses

## [0.1.5] - 2022-09-27
### Added
- `OlsClient.get_term_in_defining_ontology()` method for looking up a term by IRI/ID alone
- Improvements to tests

## [0.1.4] - 2022-09-26
### Changed
- Add more fields to `Term` schema

## [0.1.3] - 2022-09-23
### Changed
- `OlsClient` is now exported so you can do `from ols_py import OlsClient`
- `id` is not required in `SearchResultItem`, update schema

## [0.1.2] - 2022-09-23
### Added
- Add more fields to search schema (e.g. synonym)

## [0.1.1] - 2022-09-21
### Changed
- Improvements to docs

## [0.1.0] - 2022-09-21
### Added
- `OlsClient.search()` for the search endpoint
- `OlsClient.get_term_parents()`, `OlsClient.get_term_children()`, ..., for parents/children/ancestors of terms

## [0.0.3] - 2022-09-19
### Added
- Fixed docs by adding `mkdocstrings-python` dependency

## [0.0.2] - 2022-09-19
### Changed
- Initial release on PyPI

[Unreleased]: https://github.com/ahida-development/ols-py/compare/0.2.2...master
[0.2.2]: https://github.com/ahida-development/ols-py/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/ahida-development/ols-py/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/ahida-development/ols-py/compare/0.1.5...0.2.0
[0.1.5]: https://github.com/ahida-development/ols-py/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/ahida-development/ols-py/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/ahida-development/ols-py/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/ahida-development/ols-py/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/ahida-development/ols-py/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/ahida-development/ols-py/compare/0.0.3...0.1.0
[0.0.3]: https://github.com/ahida-development/ols-py/compare/0.0.2...0.0.3
[0.0.2]: https://github.com/ahida-development/ols-py/tree/0.0.2
