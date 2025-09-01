# --- STAGE 1: Build Stage ---
# This stage installs dependencies and prepares the application
FROM python:3.11.13-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies, including dos2unix for robustness
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the builder stage
COPY . /app/

# Run collectstatic. This gathers all static files (including admin files)
RUN SECRET_KEY="dummy" python manage.py collectstatic --noinput


# --- STAGE 2: Final Stage ---
# This stage creates the small, final production image
FROM python:3.11.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dos2unix in the final stage as well
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and static files from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy BOTH entrypoint scripts from the builder stage
COPY --from=builder /app/entrypoint.sh /app/entrypoint.sh
COPY --from=builder /app/entrypoint-worker.sh /app/entrypoint-worker.sh

# Forcefully convert and set permissions for BOTH scripts
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
RUN dos2unix /app/entrypoint-worker.sh && chmod +x /app/entrypoint-worker.sh

# Copy the rest of the application code
COPY . /app/

# Create the mount point for media files
RUN mkdir -p /app/media && chown -R 1000 /app/media

# Expose the port Gunicorn will run on
EXPOSE 8000

# Set the default entrypoint for the container. This will be used by the 'web' service.
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]