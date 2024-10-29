FROM python:3.10-slim-bullseye

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

COPY requirements.txt requirements.txt

RUN apt-get -qq update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python manage.py collectstatic --noinput

