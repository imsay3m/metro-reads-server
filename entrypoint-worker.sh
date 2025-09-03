#!/bin/sh

# This is the entrypoint for background worker services (Celery, Celery Beat).
# It waits for the database but does NOT run migrations to prevent race conditions.

# Exit immediately if a command exits with a non-zero status.
set -e

# The worker services only need to wait for the database to be ready.
echo "Worker: Waiting for database..."
python manage.py wait_for_db

echo "Worker: Starting process..."

# If starting Celery Beat, wait until django_celery_beat tables exist (created by web migrations)
for arg in "$@"; do
    if [ "$arg" = "beat" ]; then
        echo "Beat: Waiting for django_celery_beat tables to be ready..."
        python - <<'PY'
import os, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection

required_tables = {
    "django_celery_beat_crontabschedule",
    "django_celery_beat_periodictask",
}

max_attempts = 60
for attempt in range(1, max_attempts + 1):
    with connection.cursor() as cursor:
        existing = set(connection.introspection.table_names())
    if required_tables.issubset(existing):
        print("Beat: Required tables detected. Proceeding.")
        break
    print(f"Beat: Tables not ready yet (attempt {attempt}/{max_attempts}). Sleeping 1s...")
    time.sleep(1)
else:
    print("Beat: Proceeding without confirmation (timeout), may crash if tables missing.")
PY
        break
    fi
done
# Important: Do NOT run migrations from worker/beat to avoid race conditions.

# This special shell command means "execute the command that was passed as
# arguments to this script". In our docker-compose.yml, this will be the
# 'celery worker' or 'celery beat' command.
exec "$@"