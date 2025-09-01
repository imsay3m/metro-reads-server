# --- STAGE 1: Build Stage ---
# This stage installs dependencies and prepares the application
FROM python:3.11.13-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the builder stage
COPY . /app/

# Run collectstatic
RUN SECRET_KEY="dummy" python manage.py collectstatic --noinput


# --- STAGE 2: Final Stage ---
# This stage creates the small, final production image
FROM python:3.11.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dos2unix in the final stage for the script conversion
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix && rm -rf /var/lib/apt/lists/*

# Copy build artifacts from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /app/staticfiles /app/staticfiles
COPY --from=builder /app/entrypoint.sh /app/entrypoint.sh
COPY --from=builder /app/entrypoint-worker.sh /app/entrypoint-worker.sh

# --- THIS IS THE FIX ---
# Copy the entire application source code from the builder stage.
# This includes manage.py, the 'apps' directory, and the 'config' directory.
COPY --from=builder /app /app

# Set permissions and create media directory
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
RUN dos2unix /app/entrypoint-worker.sh && chmod +x /app/entrypoint-worker.sh
RUN mkdir -p /app/media && chown -R 1000 /app/media

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]