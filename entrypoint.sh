#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready before proceeding.
echo "Web service: Waiting for database..."
python manage.py wait_for_db

# Run database migrations
echo "Web service: Running database migrations..."
python manage.py migrate --noinput

# Create a superuser from environment variables if it doesn't exist
echo "Web service: Checking for superuser..."
python manage.py createsuperuser_from_env

# Start the application server
echo "Web service: Starting Gunicorn server..."
# Use $PORT, which is provided by platforms like Railway/Heroku.
# Gunicorn will default to 8000 if PORT is not set.
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}