# --- STAGE 1: Build Stage ---
# This stage installs dependencies and prepares the application
FROM python:3.11.13-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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
FROM python:3.11.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the collected static files from the builder stage
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy the media directory (though it will be empty on build)
COPY --from=builder /app/media /app/media

# Copy the entrypoint script
COPY --from=builder /app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application code
COPY . /app/

# Expose the port Gunicorn will run on
EXPOSE 8000

# Set the entrypoint for the container. This runs on every start.
ENTRYPOINT ["/app/entrypoint.sh"]