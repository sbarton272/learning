FROM python:3.10

# Install node and npm for jupyter extensions
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
RUN bash -c ". ~/.nvm/nvm.sh && nvm install node"

COPY poetry.lock pyproject.toml poetry.toml /learning/

WORKDIR /learning

RUN pip install poetry && poetry install
