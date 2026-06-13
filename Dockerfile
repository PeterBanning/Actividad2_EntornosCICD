FROM python:3.6-slim

RUN mkdir -p /opt/calc
WORKDIR /opt/calc

COPY requires ./
COPY pytest.ini ./
COPY pyproject.toml ./
COPY app ./app
COPY test ./test
COPY web ./web
RUN pip install -r requires
