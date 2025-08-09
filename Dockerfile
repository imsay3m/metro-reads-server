# --- STAGE 1: Build Stage ---
FROM python:3.11.13-bookworm AS builder
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies AND the 'dos2unix' utility
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ... (pip install logic is the same) ...
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
RUN SECRET_KEY="dummy" python manage.py collectstatic --noinput

# --- STAGE 2: Final Stage ---
FROM python:3.11.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dos2unix in the final stage as well
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /app/staticfiles /app/staticfiles
COPY --from=builder /app/entrypoint.sh /app/entrypoint.sh

# 1. Convert the file from Windows (dos) to Linux (unix) format.
# 2. Set the execute permission.
RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app/
RUN mkdir -p /app/media && chown -R 1000 /app/media
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]