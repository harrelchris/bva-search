#!/usr/bin/env bash

source .venv/bin/activate

set -a
source .env
set +a

dropdb --if-exists $POSTGRES_DB
dropuser $POSTGRES_USER

createuser $POSTGRES_USER
createdb $POSTGRES_DB --owner=$POSTGRES_USER

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput --username user --email user@email.com
