# base stage
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && \
    apt upgrade -y && \
    apt clean && \
    rm -rf /var/cache/apt/*

# uv stage
FROM base AS uv
ENV UV_PYTHON_PREFERENCE=only-system
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PROJECT_ENVIRONMENT=/usr/local/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PATH="/root/.local/bin:${PATH}"


FROM uv AS dev
WORKDIR /app
ENV PYTHONPATH="/app/src"
COPY pyproject.toml uv.lock ./
COPY src/exchange_rate /app/src/exchange_rate


# Production stage
FROM uv AS prod
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH="/app/src"
EXPOSE 49000

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/exchange_rate /app/src/exchange_rate

CMD ["uvicorn", "src.exchange_rate.main:app", "--host", "0.0.0.0", "--port", "49000", "--loop", "uvloop"]
