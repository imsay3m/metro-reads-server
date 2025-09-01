# --- STAGE 1: Build Stage ---
# This stage installs dependencies, builds static files, and prepares the application.
# We use the full 'bookworm' image because it contains all necessary build tools.
FROM python:3.11.13-bookworm AS builder

# Set environment variables for a clean Python environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies, including 'dos2unix' for cross-platform robustness
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment for clean dependency management
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages, copying only requirements.txt first to leverage caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project source code into the builder stage
COPY . /app/

# Run collectstatic. This gathers all static files (from your apps and Django admin)
# into the /app/staticfiles directory defined by STATIC_ROOT.
# A dummy SECRET_KEY is provided because the command requires settings to be loaded.
RUN SECRET_KEY="dummy" python manage.py collectstatic --noinput


# --- STAGE 2: Final Stage ---
# This stage creates the small, final production image
FROM python:3.11.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# We need dos2unix in the final stage to process the script
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the collected static files from the builder stage
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy the entire application source code from the builder stage.
# This includes manage.py, the 'apps' directory, 'config' directory, and entrypoint scripts.
COPY --from=builder /app /app

# Forcefully convert the entrypoint script to Unix format and make it executable.
# This makes the build immune to Windows line-ending issues.
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Create the mount point for persistent media storage (for Render/Railway)
# and set ownership for the non-root user that these platforms use.
RUN mkdir -p /app/media && chown -R 1000 /app/media

# Expose the port the application will run on
EXPOSE 8000

# Set the final entrypoint. This executes the shell interpreter '/bin/sh'
# and passes our script to it, which avoids any lingering execute permission issues.
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]