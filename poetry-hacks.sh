#!/bin/bash

PACKAGE_NAME=marine-flow

poetry new --src $PACKAGE_NAME
poetry add --group dev darglint flake8 black isort mypi nose2 nose2-cov pylint pydocstyle safety

poetry install
