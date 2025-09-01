#!/bin/sh

set -e

echo "Waiting for database to be ready..."
python manage.py wait_for_db

# Run database migrations (this is now run only by the 'web' service)
echo "Running database migrations..."
python manage.py migrate --noinput

# Create a superuser from environment variables if it doesn't exist
echo "Checking for superuser..."
python manage.py createsuperuser_from_env

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000