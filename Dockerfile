FROM python:3.12.0a6-alpine3.17
MAINTAINER DoPureCode
ENV PYTHONUNBUFFERED 1

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app

RUN adduser -D user
USER user