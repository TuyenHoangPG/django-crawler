FROM python:3.9.2

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean -y && \
    apt-get install -y cron && \
    apt-get install -y --no-install-recommends apt-utils tar git build-essential python3 python3-pip python3-setuptools python3-dev net-tools

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /var/log/uwsgi
RUN mkdir /api

COPY . /api

WORKDIR /api

RUN pip install --upgrade pip
RUN pip install uwsgi
RUN pip install --no-cache-dir -r ./requirements/requirements.txt

EXPOSE 5000
