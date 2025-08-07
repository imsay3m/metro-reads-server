#!/bin/sh

set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# --- NEW COMMAND ---
# Create a superuser from environment variables if it doesn't exist
echo "Checking for superuser..."
python manage.py createsuperuser_from_env

# Start the application
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000