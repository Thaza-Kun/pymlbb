# For testing purposes
FROM ghcr.io/astral-sh/uv:alpine3.23

COPY api /api

# COPY asset /asset

# COPY static/mlbb.example.sqlite static/mlbb.sqlite

WORKDIR /api

RUN uv sync

CMD ["uv", "run", "fastapi", "run", "--port", "4320"]
