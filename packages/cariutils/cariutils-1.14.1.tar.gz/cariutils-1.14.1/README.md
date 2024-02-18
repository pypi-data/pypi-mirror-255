# cariutils - Carium Python Utilities

Collection of common Python utilities

## Installation

[poetry](https://python-poetry.org/) is required.  Follow the recommended [installation](https://python-poetry.org/docs/#installation) method via [pipx](https://pipx.pypa.io/stable/).

```bash
pipx install poetry
```

poetry can install the module in the local virtualenv `.venv`
```bash
make prepare-venv
```

## Development and Test

```bash
unset DJANGO_SETTINGS_MODULE
make test
```

## Publish to PyPI

set the publishing token to `POETRY_PYPI_TOKEN_PYPI`
Build and release
```
 export POETRY_PYPI_TOKEN_PYPI=<api token>
make publish
```
