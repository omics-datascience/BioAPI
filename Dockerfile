FROM python:3.12.0-alpine3.18

COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /uvx /bin/

ENV MONGO_HOST "mongo_bioapi"
ENV MONGO_PORT 27017
ENV MONGO_USER "bioapi"
ENV MONGO_PASSWORD "bioapi"
ENV MONGO_DB "bio_api"
ENV UV_COMPILE_BYTECODE 1
ENV UV_LINK_MODE copy
ENV PATH="/app/.venv/bin:$PATH"

# The number of gunicorn's worker processes for handling requests.
ENV WEB_CONCURRENCY 1

# Installs Python dependencies
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Flask app
COPY ./bio-api /app

# Creates logs directory
RUN mkdir /logs

# Runs Gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "bioapi:app", "--timeout", "3600"]
