#!/usr/bin/env bash

set -e

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip

pip install ruff

pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp envs/local.env .env
fi
