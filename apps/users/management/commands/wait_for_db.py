import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """
    Django command to pause execution until the database is available.
    """

    help = "Waits for the database to become available."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        attempts = 0
        max_attempts = 30  # Try for 30 seconds

        while not db_conn and attempts < max_attempts:
            try:
                # Get the default database connection
                db_conn = connections["default"]
                # Try to establish a connection
                db_conn.cursor()
            except OperationalError:
                self.stdout.write(
                    self.style.WARNING("Database unavailable, waiting 1 second...")
                )
                time.sleep(1)

            attempts += 1

        if db_conn:
            self.stdout.write(
                self.style.SUCCESS("Database available! Connection successful.")
            )
        else:
            self.stdout.write(
                self.style.ERROR("Database unavailable after 30 seconds. Exiting.")
            )
            # Exit with a non-zero status code to make the deploy fail
            exit(1)
