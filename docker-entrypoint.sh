#!/bin/sh

echo running migrations
python src/manage.py migrate

# echo mocking
# python src/manage.py mock_data --clear True --number 60

echo running server
python src/manage.py runserver 0.0.0.0:8000