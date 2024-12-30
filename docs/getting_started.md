# Getting Started

## Installation

It is reccomended to install the package in a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

Alternatively, you can also use [`conda`] or [`mamba`] to create a new environment.

```bash
conda create -n sunflare python=3.10
conda activate sunflare
```

The package is available on [PyPI].

```bash
pip install sunflare
```

Alternatively, you can also install the package from source by cloning the [repository].

```bash
git clone https://github.com/redsun-acquisition/sunflare.git
cd sunflare
pip install -e .
```

## Usage from source

### Building the documentation

If you want to build the documentation locally, you'll need to install the dependencies first:

```bash
pip install -e .[dev]
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

You can get a coverage report by running the following command:

```bash
pytest --cov=sunflare --cov-report=html
```

This will generate a `htmlcov` directory with the coverage report, which you can open in your browser by opening the `index.html` file.

[conda]: https://docs.conda.io/en/latest/
[mamba]: https://mamba.readthedocs.io/en/latest/
[repository]: https://github.com/redsun-acquisition/sunflare
[pypi]: https://pypi.org/project/sunflare/
