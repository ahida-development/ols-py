# ols-py

[![PyPI](https://img.shields.io/pypi/v/ols-py?style=flat-square)](https://pypi.python.org/pypi/ols-py/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ols-py?style=flat-square)](https://pypi.python.org/pypi/ols-py/)
[![PyPI - License](https://img.shields.io/pypi/l/ols-py?style=flat-square)](https://pypi.python.org/pypi/ols-py/)
[![Tests][github actions badge]][github actions page]
[![Coookiecutter - Wolt](https://img.shields.io/badge/cookiecutter-Wolt-00c2e8?style=flat-square&logo=cookiecutter&logoColor=D4AA00&link=https://github.com/woltapp/wolt-python-package-cookiecutter)](https://github.com/woltapp/wolt-python-package-cookiecutter)

[github actions badge]: https://github.com/ahida-development/ols-py/workflows/Test/badge.svg
[github actions page]: https://github.com/ahida-development/ols-py/actions?workflow=test

---

**Documentation**: [https://ahida-development.github.io/ols-py](https://ahida-development.github.io/ols-py)

**Source Code**: [https://github.com/ahida-development/ols-py](https://github.com/ahida-development/ols-py)

**PyPI**: [https://pypi.org/project/ols-py/](https://pypi.org/project/ols-py/)

---

Python client for the [Ontology Lookup Service](https://www.ebi.ac.uk/ols4)

**Current status:**

* Now that OLS4 is released and OLS3 is no longer updated, this client will only
  support OLS4 going forward
* Some API endpoints may not be implemented, or schemas not fully described -
  please [open an issue](https://github.com/ahida-development/ols-py/issues) if
  you want anything added.

Features:

* Type annotated so you know which parameters can be used for each endpoint
* Responses validated and parsed with [pydantic](https://github.com/pydantic/pydantic) for
  easy access to response data

## Example usage

```python
from ols_py.client import Ols4Client
client = Ols4Client()
resp = client.search("MC1R", params={"ontology": "go"})
term = resp.response.docs[0]
print(term)
# SearchResultItem(
#   id=None, annotations=None, annotations_trimmed=None,
#   description=['A rhodopsin-like G-protein ... gamma-melanocyte-stimulating hormone.'],
#   iri='http://purl.obolibrary.org/obo/PR_000001146', label='melanocortin receptor',
#   obo_id='PR:000001146', ontology_name='go', ontology_prefix='GO', subset=None,
#   short_form='PR_000001146', synonyms=None, type='class'
#)
print(term.iri)
# http://purl.obolibrary.org/obo/PR_000001146
```

## Installation

```sh
pip install ols-py
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.10+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github project page
 ](https://pages.github.com/) automatically as part each release.

### Releasing

Trigger the [Draft release workflow](https://github.com/ahida-development/ols-py/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/ahida-development/ols-py/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/ahida-development/ols-py/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Pre-commit

Pre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```

---

This project was generated using the [wolt-python-package-cookiecutter](https://github.com/woltapp/wolt-python-package-cookiecutter) template.
