#!/bin/sh

set -e

echo "Web service: Waiting for database..."
python manage.py wait_for_db

# The 'web' service is now solely responsible for running migrations.
echo "Web service: Running database migrations..."
python manage.py migrate --noinput

echo "Web service: Checking for superuser..."
python manage.py createsuperuser_from_env

echo "Web service: Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000