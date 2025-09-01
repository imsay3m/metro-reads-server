#!/bin/sh

# This is the entrypoint for background worker services (Celery, Celery Beat).
# It waits for the database but does NOT run migrations to prevent race conditions.

# Exit immediately if a command exits with a non-zero status.
set -e

# The worker services only need to wait for the database to be ready.
echo "Worker: Waiting for database..."
python manage.py wait_for_db

echo "Worker: Starting process..."
# This special shell command means "execute the command that was passed as
# arguments to this script". In our docker-compose.yml, this will be the
# 'celery worker' or 'celery beat' command.
exec "$@"