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

# Install dos2unix in the final, slim image as well
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and static files from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /app/staticfiles /app/staticfiles

# --- THIS IS THE WORKAROUND ---
# Instead of copying from the builder, copy the scripts directly from the build context.
# This makes the final image slightly less independent but avoids the syntax error.
COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./entrypoint-worker.sh /app/entrypoint-worker.sh

# Forcefully convert and set permissions
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
RUN dos2unix /app/entrypoint-worker.sh && chmod +x /app/entrypoint-worker.sh

RUN mkdir -p /app/media && chown -R 1000 /app/media
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]