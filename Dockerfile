FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get install -y libmariadb-dev

COPY . /app

RUN pip install fastapi uvicorn mariadb
