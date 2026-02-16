# Run tests

This guide shows you how to run the Sunflare test suite and generate coverage reports.

## Prerequisites

Make sure you have [installed Sunflare with development dependencies](installation.md#install-development-dependencies).

## Run all tests

You can run the tests by running the following command from the project root:

```bash
pytest
```

## Generate coverage reports

You can obtain a test coverage report by running:

```bash
pytest --cov=sunflare --cov-report=html
```

This will generate an `htmlcov/` directory with the test coverage report. Open `htmlcov/index.html` in your browser to view it.

## Run tests on multiple Python versions

`sunflare` provides a `noxfile.py` to run tests with `nox` on all supported Python versions.

If you use `uv`, you can run tests as follows:

```bash
# Install nox globally
uv tool install nox

# Run tests on all Python versions
nox -s tests
```

This will test against all supported Python versions (3.10, 3.11, 3.12, 3.13).


## Verbose output

For more detailed output, use the `-v` flag:

```bash
pytest -v
```

## Stop on First Failure

To stop at the first failing test:

```bash
pytest -x
```

## Next Steps

- [Build the documentation](build-docs.md)
- [`sunflare` architecture](../explanation/architecture/index.md)
- [API reference](../reference/api/config.md)
