FROM python:3.9-slim-buster

WORKDIR /web

COPY requirements.txt /web/
RUN pip install -r requirements.txt

COPY . /web/
