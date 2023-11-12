FROM python:3.11 AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN pip install --upgrade pip

WORKDIR ${APP_HOME}

COPY ./requirements.txt ${APP_HOME}/

RUN pip3 install --no-cache-dir -r requirements.txt

RUN apk del .build-deps

COPY . ${APP_HOME}/