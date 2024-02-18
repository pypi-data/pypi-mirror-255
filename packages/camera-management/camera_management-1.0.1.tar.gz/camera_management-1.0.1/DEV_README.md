# Contributing to camera-management

This documents aims to describe the basic setup and code style for development.

## Setup

This project supports python 3.10. It runs on Windows 10 (untested), Ubuntu 22.04 (untested) and macOS Ventura 13.5.

The use of an virtual environment is recommended:

```bash
git clone https://github.com/TrafoToolkit/camera-management.git
python3 -m venv PATH_TO_REPO/.venv
source PATH_TO_REPO/.venv/bin/activate
```

Install requirements and camera-management as package:

```bash
pip install -r requirements.txt
pip install -e PATH_TO_REPO
```

### Code style

The project is using Black formatter, linter Flake8, automated import sorting, automated checker for code documentation,
checker for python code.

All these actions are automated by CI and pre-commit git hooks.

To setup the pre-commit hooks run from the root folder of the project:

```bash
pre-commit install
```

This will add pre-commit script hook to .git/hooks based on `.pre-commit-config.yaml`. This will cause the checks to be
run every time a commit is tried. The checks will be applied only to the staged content. If not all checks pass, the
commit will be rejected. Please fix the issues and try again.

__NOTE:__ In case you would like to run pre-commit checkers against the whole project, then just execute:

```bash
pre-commit run --all-files
```
