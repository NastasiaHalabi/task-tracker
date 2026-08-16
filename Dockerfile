# syntax=docker/dockerfile:1

# ---- builder ----
FROM python:3.11-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim AS runtime

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /usr/sbin/nologin --create-home app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app

RUN chown -R app:app /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
