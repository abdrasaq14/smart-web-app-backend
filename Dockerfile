FROM python:3.12-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client \
		libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/base.txt
RUN pip install --no-cache-dir -r requirements/development.txt

# Freeze versions into a requirements.lock file
RUN pip freeze > requirements.lock

WORKDIR /api
COPY . .

EXPOSE 8000
# CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"] 
ENTRYPOINT ["/bin/sh", "docker-entrypoint.sh"]
# dont push dev
# gunicorn for prod
# port 80
