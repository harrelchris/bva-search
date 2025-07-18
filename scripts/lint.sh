#!/usr/bin/env bash

set -e

source .venv/bin/activate

ruff format

ruff check --fix
