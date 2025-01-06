FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    rsync \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry
WORKDIR /watchsync
COPY pyproject.toml .
COPY .pre-commit-config.yaml .
COPY setup.cfg .
COPY README.md .
COPY watchsync ./watchsync
COPY tests ./tests
RUN poetry install --with dev
RUN git init
CMD ["sh", "-c", "poetry run pre-commit run --all-files && poetry run coverage run -m unittest discover -s tests && poetry run coverage report"]
