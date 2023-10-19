#!/usr/bin/env bash

# https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin
# -e  Exit immediately if a command exits with a non-zero status.
# -x Print commands and their arguments as they are executed.
set -e

rm example/db.sqlite3 || true
python example/manage.py migrate
python example/manage.py createsuperuser --noinput
python example/manage.py runserver 0.0.0.0:${DJANGO_BIND_PORT:-8080}
