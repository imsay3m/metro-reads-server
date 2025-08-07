import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """
    Creates a superuser from environment variables.
    Reads: ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FIRST_NAME, ADMIN_LAST_NAME.
    """

    help = "Creates a superuser non-interactively from environment variables."

    def handle(self, *args, **options):
        # Read all required credentials from environment variables
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        first_name = os.getenv("ADMIN_FIRST_NAME")
        last_name = os.getenv("ADMIN_LAST_NAME")

        # Check if all necessary variables are set
        if not all([email, password, first_name, last_name]):
            self.stdout.write(
                self.style.ERROR(
                    "Missing one or more required environment variables: ADMIN_EMAIL, "
                    "ADMIN_PASSWORD, ADMIN_FIRST_NAME, ADMIN_LAST_NAME. Skipping superuser creation."
                )
            )
            return

        # Check if the user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"A superuser with the email {email} already exists. Skipping creation."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Creating superuser: {first_name} {last_name} ({email})"
                )
            )

            # Pass all fields to the create_superuser method
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
