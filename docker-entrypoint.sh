#!/bin/sh

echo running migrations
python src/manage.py migrate

echo running server
python src/manage.py runserver 0.0.0.0:8000