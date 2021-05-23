FROM python:3.9.5-slim
COPY . /trev
WORKDIR trev

RUN apt-get update
RUN apt-get install gcc

RUN pip3 install -r requirements.txt

CMD python3 main.py