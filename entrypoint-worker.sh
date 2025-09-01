#!/bin/sh

set -e

# The worker services only need to wait for the database to be ready.
echo "Worker: Waiting for database..."
python manage.py wait_for_db

echo "Worker: Starting process..."
# This command executes whatever command is passed to this script.
# For our Celery services, this will be the 'celery worker' or 'celery beat' command.
exec "$@"