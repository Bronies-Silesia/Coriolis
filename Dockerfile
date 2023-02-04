FROM python:3.11

WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
COPY poetry.lock pyproject.toml ./
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && poetry install

COPY . .

ENTRYPOINT ["./run.sh"]
