FROM python:3.10-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

WORKDIR /code

RUN rm -rf .venv

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN ln -s $HOME/.local/bin/poetry /usr/bin/poetry

WORKDIR $PYSETUP_PATH

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

WORKDIR /code/casino-api

EXPOSE 8000

CMD ["poetry", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000", "--reload"]
