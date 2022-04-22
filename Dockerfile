# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git gcc python3-dev
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY start /start
CMD ["/bin/bash", "/start"]
