FROM python:slim
LABEL authors="blockmento"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD app .

ENTRYPOINT ["python3", "./main.py"]