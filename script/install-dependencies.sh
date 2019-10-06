#!/usr/bin/env bash
set -ex

[[ "$CI" = true ]] || [[ -n "$GITHUB_ACTIONS" ]] || [[ -n "$VIRTUAL_ENV" ]] || exit 1

python --version
python -m pip install --disable-pip-version-check --upgrade pip setuptools
python -m pip install --upgrade -r dev-requirements.txt
python -m pip install pycountry
python -m pip install -e .
