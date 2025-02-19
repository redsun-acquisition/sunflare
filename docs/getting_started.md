# Getting Started

## Installation

It is reccomended to install the package in a virtual environment.

::::{tab-set}
:::{tab-item} venv
```{code-block} shell
# python version depends
# on the globally installed python
python -m venv sunflare-env

venv\Scripts\activate

# for Windows...
# ... command prompt
venv\Scripts\activate.bat

# ... powershell
venv\Scripts\Activate.ps1
```
:::
:::{tab-item} conda
```{code-block} shell
conda create -n redsun-env python=3.9
conda activate redsun-env
```
:::
:::{tab-item} mamba
```{code-block} shell
mamba create -n redsun-env python=3.9
mamba activate redsun-env
```
:::
::::

You can install the package from [PyPI] or directly from the GitHub [repository].

::::{tab-set}
:::{tab-item} PyPI
```{code-block} shell
pip install -U sunflare
```
:::
:::{tab-item} GitHub
```{code-block} shell
git clone https://github.com/redsun-acquisition/sunflare.git
cd sunflare
pip install -e .
```
:::
::::

## Usage from source

### Building the documentation

If you want to build the documentation locally, you'll need to install the dependencies first:

```bash
pip install -e .[doc]
```

You can build the documentation by running the following command:

```bash
cd docs
make html

# for windows
make.bat html
```

And then open the `_build/html/index.html` file in your browser.

### Running tests

To run the tests, you'll need to install the dependencies first:

```bash
pip install -e .[dev]
```

Then, you can run the tests by running the following command:

```bash
pytest
```

This will automatically generate a `htmlcov` directory with the test coverage report, which you can open in your browser by opening the `index.html` file.

[conda]: https://docs.conda.io/en/latest/
[mamba]: https://mamba.readthedocs.io/en/latest/
[repository]: https://github.com/redsun-acquisition/sunflare
[pypi]: https://pypi.org/project/sunflare/
