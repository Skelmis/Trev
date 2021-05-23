FROM python:3.9.5
COPY . /trev
WORKDIR trev

RUN pip3 install -r requirements.txt

CMD python3 main.py