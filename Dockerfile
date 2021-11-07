FROM python:3.9-slim-bullseye as common-base

FROM common-base
COPY . /trev
WORKDIR trev

RUN pip3 install -r requirements.txt

CMD python3 main.py