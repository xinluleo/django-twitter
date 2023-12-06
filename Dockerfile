FROM python:3.10.8-slim-bullseye
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip \
    && pip install mysqlclient
RUN mkdir /code
WORKDIR /code
COPY requirements-prd.txt /code/
RUN pip install -r requirements-prd.txt
COPY . /code/