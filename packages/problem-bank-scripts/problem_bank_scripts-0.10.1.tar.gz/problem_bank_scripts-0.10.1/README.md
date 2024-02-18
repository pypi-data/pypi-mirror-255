# Problem Bank Scripts 

[![Python](https://img.shields.io/badge/python-3.9-blue)]()
[![codecov](https://codecov.io/gh/open-resources/problem_bank_scripts/branch/main/graph/badge.svg)](https://codecov.io/gh/open-resources/problem_bank_scripts)
[![Documentation Status](https://readthedocs.org/projects/problem_bank_scripts/badge/?version=latest)](https://problem_bank_scripts.readthedocs.io/en/latest/?badge=latest)


## Installation

```bash
$ pip install -i https://test.pypi.org/simple/ problem_bank_scripts
```

## Update version

Here are the steps to increment the version (replace patch with major/minor/patch)

```
poetry version patch

pico src/problem_bank_scripts/__init__.py

pico tests/test_problem_bank_scripts.py

poetry run pytest

cd docs; poetry run make html; cd ..

git add .; git commit -m "increment version"; git push

poetry build

poetry publish
```


## Features

- TODO

## Dependencies

- TODO

## Usage

- TODO

## Documentation

The official documentation is hosted on Read the Docs: https://problem_bank_scripts.readthedocs.io/en/latest/

## Contributors

We welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/open-resources/problem_bank_scripts/graphs/contributors).

### Credits

This package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).
