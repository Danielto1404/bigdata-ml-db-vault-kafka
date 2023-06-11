FROM python:3.9.6-slim

ENV PYTHONUNBUFFERED 1

RUN pip install hvac==1.1.0

WORKDIR /app

ADD . /app