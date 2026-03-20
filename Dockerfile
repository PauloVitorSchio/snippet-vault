# ============================================================
# base — shared runtime foundation
# ============================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system appuser && useradd --system --gid appuser --create-home appuser

WORKDIR /app

RUN chown appuser:appuser /app

# ============================================================
# dev — hot-reload development server
# ============================================================
FROM base AS dev

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

USER appuser

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

# ============================================================
# builder — installs production deps into /app/.venv
# ============================================================
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# ============================================================
# prod — lean production image (no build tools)
# ============================================================
FROM base AS prod

COPY --from=builder /app/.venv /app/.venv

COPY --chown=appuser:appuser . /app/

USER appuser

CMD ["/app/.venv/bin/gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "30", \
     "--access-logfile", "-"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
