#!/bin/sh

echo hello world
python src/manage.py migrate
python src/manage.py mock_data --clear True --number 60
python src/manage.py runserver 0.0.0.0:8000