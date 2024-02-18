# Ingots

The framework for developing different web-services (asynchronous) and reusable components for them.

## For consumers

### Installation

For using the framework just execute the following commands:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install ingots
```


## For developers

### Cloning the project

Execute the following commands:
```bash
mkdir ingots-libs
cd ingots-libs
git clone https://github.com/ABKorotky/ingots.git
cd ingots
```

### Prepare a virtual environment

Execute the following commands:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Prepare repository hooks

Execute the following commands:
```bash
pre-commit autoupdate
pre-commit install
```

Configure the `Sphinx` tool:
Please, use the following page for configuring the Sphinx documentation generator: [Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html)
```bash
sphinx-build -b html docs docs/build -v
```

### Using the tox tool

The project has some automation via the `tox` tool.

Use the `tox` tool for the following activities:

`tox -e reformat` - auto reformat code by the black tool, makes ordering import too.

`tox -e cs` - checks code style by PEP8.

`tox -e ann` - checks annotations of types by the mypy tool.

`tox -e utc` - runs unittests with the coverage tool.

`tox -e report` - builds coverage report for the project.

`tox -e doc` - builds a package documentation.

`tox -e build` - builds a package form current branch / tag / commit.

`tox -e upload` - uploads package to the PyPI index. Set the `PYPI_REPOSITORY_ALIAS` environment variable for specifying PyPI destination.

Calling tox without parameters will execute the following steps: **cs**, **ann**, **utc** and **report**.
