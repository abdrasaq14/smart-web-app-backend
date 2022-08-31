# Smarterise - api

## Requirements

1. [Docker](https://www.docker.com/products/docker-desktop/)
2. [Python 3.9](https://www.python.org/downloads/)
3. Virtual environment of choice (virtualenv, venv, virtualenvwrapper...)
4. [Pytest](https://docs.pytest.org/en/7.1.x/)

## How to install

1. Create a virtual environment matching the Python version `python3.9 -m venv venv`
2. Start the virtual environment: `source venv/bin/activate`
3. Run `make requirements`
4. Generate your own .env file by doing `cp .env.example src/.env`
5. Source the .env file by running `source src/.env`
6. Run `docker compose up` starts the docker or `docker compose up -d` starts the docker without
   the logs.
7. Run `make migrate` runs the migrations or `python src/manage.py migrate`.
8. Create a superuser by running `python src/manage.py createsuperuser` and use the email added to `.env`.
9. Run `make run` starts the development server or `python src/manage.py runserver`.


## Swagger API

1. `http://localhost:8000/swagger/redoc` - In development mode shows the apis in redoc format.
2. `http://localhost:8000/swagger/` - In development mode, shows the apis in swagger format.


## Testing

The app uses pytest.

1. `make test` runs all the tests
