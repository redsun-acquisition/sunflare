# Build Documentation

This guide shows you how to build the Sunflare documentation locally.

## Prerequisites

Make sure you have [installed Sunflare with development dependencies](installation.md#install-development-dependencies).

## Build with Material for MkDocs

You can build the documentation by running the following command from the project root:

```bash
uv run mkdocs build
```

The built documentation will be in the `site/` directory. Open `site/index.html` in your browser to view it.

## Serve Documentation Locally

For development, you can serve the documentation with live reload:

```bash
uv run mkdocs serve
```

This will start a local server at `http://localhost:8000` and automatically rebuild the documentation when you make changes.

## Deploy Versioned Documentation

Sunflare uses [mike](https://github.com/jimporter/mike) for multi-version documentation. To deploy a new version:

```bash
# Deploy version 0.8.0 and tag it as 'latest'
uv run mike deploy 0.8.0 latest --update-aliases

# Set the default version
uv run mike set-default latest

# List all deployed versions
uv run mike list

# Serve all versions locally
uv run mike serve
```

The versioned documentation is deployed to the `gh-pages` branch and hosted on GitHub Pages.

## Troubleshooting

### Missing Dependencies

If you get errors about missing dependencies, make sure you've installed the development dependencies:

```bash
uv sync
```

### Port Already in Use

If port 8000 is already in use, you can specify a different port:

```bash
uv run mkdocs serve --dev-addr localhost:8080
```

### Cross-Reference Warnings

If you see warnings about missing cross-reference targets during build, verify that:

1. The Python module/class/function exists in the codebase
2. The docstring format is correct (NumPy style)
3. The mkdocstrings configuration in `mkdocs.yml` is correct

## Next Steps

- Learn how to [run tests](run-tests.md)
- Read about [Sunflare's architecture](../explanation/architecture/index.md)
