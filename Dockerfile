# --- STAGE 1: Build Stage ---
# Use a specific, modern version of Python on Debian Bookworm
FROM python:3.11.13-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies required for building Python packages
# This step is cached and only runs if this line changes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc

# Copy the requirements file
COPY requirements.txt /app/

# Install python dependencies into a virtual environment for a clean setup
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt --ignore-version


# --- STAGE 2: Final Stage ---
# Start from the slim image for a smaller final footprint
FROM python:3.11.13-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy the project code into the container
COPY . /app/

# Copy the new startup script into the container
COPY ./entrypoint.sh /app/entrypoint.sh
# Make sure the script is executable inside the container
RUN chmod +x /app/entrypoint.sh

# Expose the port Gunicorn will run on
EXPOSE 8000

# Command to run the application. REMOVE the old CMD instruction. The entrypoint script will now handle starting Gunicorn.
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
