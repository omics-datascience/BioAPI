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

# MCP SDK and runtime dependencies. These are installed into the system Python
# used by the dedicated MCP service, leaving the web service venv unchanged.
COPY sdk/pyproject.toml sdk/uv.lock /app/sdk/
COPY sdk/src /app/sdk/src
RUN cd /app/sdk \
    && uv export --frozen --no-cache --no-dev --extra mcp --format requirements.txt --no-emit-project --output-file /tmp/bioapi-sdk-mcp-requirements.txt \
    && uv pip install --system --no-cache --requirements /tmp/bioapi-sdk-mcp-requirements.txt \
    && rm /tmp/bioapi-sdk-mcp-requirements.txt

# Flask app
COPY ./bio-api /app

# Installs curl for container health checks and creates the logs directory.
RUN apk add --no-cache curl \
    && mkdir /logs

# Runs Gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "bioapi:app", "--timeout", "3600"]
