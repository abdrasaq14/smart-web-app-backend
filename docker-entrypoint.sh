#!/bin/sh

python src/manage.py migrate
make mock
python src/manage.py runserver 0.0.0.0:8000