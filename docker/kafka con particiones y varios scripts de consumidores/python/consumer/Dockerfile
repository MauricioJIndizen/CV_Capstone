# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

COPY . .

CMD ["python","consumer_main.py"]