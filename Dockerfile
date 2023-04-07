FROM python:3.10-alpine
MAINTAINER test_user

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev
RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN adduser -D user
USER user