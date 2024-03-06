FROM python:3.10.12-alpine

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "server.py"]