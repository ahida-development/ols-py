# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Unified OLS3 and OLS4 schemas - OLS4 is more in sync with OLS3 now, so separate schemas are no longer needed
- `mypy` is now happy with our types thanks to the unified schemas! We can keep the code type-checked from now on
- Implemented more endpoints, e.g. retrieving individuals and properties
- Reworked function arguments - any optional parameters for requests are now
specified with `TypedDict`, rather than a PyDantic object - this is more user-friendly


## [0.5.1] - 2023-09-14
### Changed
- Added types/schemas for `obo_synonym` and `obo_xref` on Term responses

## [0.5.0] - 2023-07-27
### Changed
- Updated to [Pydantic V2](https://docs.pydantic.dev/latest/): the new version has useful features such as multiple aliases for fields
- In Pydantic V2, url fields are stored as a URL class and cannot be directly used as strings - use `str(model.url_field)` to use them as string.

### Fixed
- Updated some schema fields to reflect latest changes to OLS4 - still a bit of a moving target!

## [0.3.0] - 2023-06-05
### Added
- Experimental support for [OLS4](https://www.ebi.ac.uk/ols4) instances (using the current
  API). OLS4 should support the same API, but currently a few responses seem
  to have a different structure, so start implementing and testing against it.

  To use the OLS4 instance, import `Ols4Client` from `ols_py.ols4_client`

## [0.2.7] - 2023-05-25
### Changed
- Allow arbitrary annotations in search queryFields

## [0.2.6] - 2023-05-17
### Added
- `get_term_hierarchical_parents()` method

## [0.2.5] - 2022-11-23
### Added
- `OlsClient.get_terms()` endpoint for multiple terms/lookup by OBO ID
- `instances` module with URLs for known instances

## [0.2.4] - 2022-11-07
### Changed
- Add "subset" to search query fields

## [0.2.3] - 2022-10-20
### Changed
- Improvements to schemas for search

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

[Unreleased]: https://github.com/ahida-development/ols-py/compare/0.5.1...master
[0.5.1]: https://github.com/ahida-development/ols-py/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/ahida-development/ols-py/compare/0.3.0...0.5.0
[0.3.0]: https://github.com/ahida-development/ols-py/compare/0.2.7...0.3.0
[0.2.7]: https://github.com/ahida-development/ols-py/compare/0.2.6...0.2.7
[0.2.6]: https://github.com/ahida-development/ols-py/compare/0.2.5...0.2.6
[0.2.5]: https://github.com/ahida-development/ols-py/compare/0.2.4...0.2.5
[0.2.4]: https://github.com/ahida-development/ols-py/compare/0.2.3...0.2.4
[0.2.3]: https://github.com/ahida-development/ols-py/compare/0.2.2...0.2.3
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
