#!/bin/sh

set -e

# The worker services only need to wait for the database to be ready.
# They DO NOT run migrations.
echo "Worker: Waiting for database..."
python manage.py wait_for_db

# This special command means "execute the command that was passed to this script".
# In our docker-compose.yml, this will be the 'celery worker' or 'celery beat' command.
exec "$@"