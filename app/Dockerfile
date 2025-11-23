FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

COPY app/ /app/

FROM builder as test

ENV DATABASE_URL=sqlite:///:memory: \
    TESTING=true

RUN python -m pytest tests/ -v --tb=short

FROM python:3.11-slim as final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /seed && \
    chown -R appuser:appuser /app /seed

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /root/.local /root/.local
COPY --from=builder --chown=appuser:appuser /app /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

CMD ["python", "src/app.py"]
