# Installation

This guide shows you how to install Sunflare in different environments.

## Create a Virtual Environment

It is recommended to install the package in a virtual environment.

=== "uv (recommended)"

    ```bash
    uv venv --python 3.10

    # For Linux/macOS
    source .venv/bin/activate

    # For Windows Command Prompt
    .venv\Scripts\activate.bat

    # For Windows PowerShell
    .venv\Scripts\Activate.ps1
    ```

=== "venv"

    ```bash
    # Python version depends on the globally installed Python
    python -m venv sunflare-env

    # For Linux/macOS
    source sunflare-env/bin/activate

    # For Windows Command Prompt
    sunflare-env\Scripts\activate.bat

    # For Windows PowerShell
    sunflare-env\Scripts\Activate.ps1
    ```

=== "conda"

    ```bash
    conda create -n sunflare-env python=3.10
    conda activate sunflare-env
    ```

=== "mamba"

    ```bash
    mamba create -n sunflare-env python=3.10
    mamba activate sunflare-env
    ```

## Install Sunflare

You can install the package from [PyPI](https://pypi.org/project/sunflare/) or directly from the GitHub [repository](https://github.com/redsun-acquisition/sunflare).

=== "PyPI"

    ```bash
    pip install -U sunflare

    # Or if you're using uv
    uv pip install sunflare
    ```

=== "GitHub (Development)"

    ```bash
    git clone https://github.com/redsun-acquisition/sunflare.git
    cd sunflare
    pip install -e .
    ```

## Install Development Dependencies

If you're contributing to Sunflare or want to run tests locally, install the development dependencies via [PEP-735](https://peps.python.org/pep-0735/) dependency groups.

=== "uv (recommended)"

    ```bash
    # Dev dependencies are automatically synchronized
    uv sync
    ```

=== "pip"

    ```bash
    pip install -e .[dev]
    ```

## Next Steps

- Learn how to [build the documentation](build-docs.md)
- Learn how to [run tests](run-tests.md)
- Check out the [tutorials](../tutorials/index.md) to get started with Sunflare
