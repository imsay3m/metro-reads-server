#!/bin/sh

set -e

echo "Waiting for database to be ready..."
python manage.py wait_for_db

echo "Running database migrations..."
# Try migrations, and if the migrations table is borked, fix and retry
if ! python manage.py migrate --noinput --fake-initial; then
    echo "Migrations failed - attempting to repair django_migrations objects and retry..."
    python - <<'PY'
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection

sql_statements = [
    "DROP SEQUENCE IF EXISTS public.django_migrations_id_seq CASCADE;",
    "DROP TABLE IF EXISTS public.django_migrations CASCADE;",
]

with connection.cursor() as cursor:
    for stmt in sql_statements:
        try:
            cursor.execute(stmt)
            print(f"Executed: {stmt}")
        except Exception as exc:
            print(f"Ignoring error executing '{stmt}': {exc}")
PY
    echo "Retrying database migrations..."
    python manage.py migrate --noinput --fake-initial
fi

# Create a superuser from environment variables if it doesn't exist
echo "Checking for superuser..."
python manage.py createsuperuser_from_env

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000