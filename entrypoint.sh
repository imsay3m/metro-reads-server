#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Container starting... Waiting for database to be ready..."
python manage.py wait_for_db

echo "Running database migrations..."
python manage.py migrate --noinput

exec "$@"