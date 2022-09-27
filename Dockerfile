FROM python:3.9.13-slim-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/base.txt
RUN pip install --no-cache-dir -r requirements/development.txt

WORKDIR /api
COPY . .

EXPOSE 8000
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]