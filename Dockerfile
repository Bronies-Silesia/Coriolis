FROM python:3.11

RUN apt-get update && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
COPY poetry.lock pyproject.toml ./
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && poetry install

COPY . .

ENTRYPOINT ["./run.sh"]
