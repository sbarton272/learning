FROM python:3.10

COPY poetry.lock pyproject.toml poetry.toml /learning/

WORKDIR /learning

RUN pip install poetry && poetry install
