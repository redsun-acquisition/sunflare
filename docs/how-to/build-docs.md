# Build documentation

This guide shows you how to build the Sunflare documentation locally.

## Prerequisites

Make sure you have [installed `sunflare` with development dependencies](installation.md#install-development-dependencies).

## Build with `zensical`

You can build the documentation by running the following command from the project root:

```bash
uv run mkdocs build
```

The built documentation will be in the `site/` directory. Open `site/index.html` in your browser to view it.

## Serve documentation locally

For development, you can serve the documentation with live reload:

```bash
uv run zensical serve
```

This will start a local server at `http://localhost:8000` and automatically rebuild the documentation when you make changes.

## Troubleshooting

### Missing dependencies

If you get errors about missing dependencies, make sure you've installed the development dependencies:

```bash
uv sync
```

### Port already in use

If port 8000 is already in use, you can specify a different port:

```bash
uv run zensical serve --dev-addr localhost:8080
```

## Next Steps

- Learn how to [run tests](run-tests.md)
- Read about [`sunflare` architecture](../explanation/architecture/index.md)
