FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y build-essential python3-dev gcc g++

COPY . /trev
WORKDIR trev

RUN pip3 install -r requirements.txt

CMD python3 main.py