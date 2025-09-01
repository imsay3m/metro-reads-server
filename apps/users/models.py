from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.academic.models import Department


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # --- MODIFIED LOGIC ---
        # We now explicitly set the defaults required for a superuser to be useful.
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # This is the key change: ensure superusers are always active and verified.
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("role") != "ADMIN":
            raise ValueError("Superuser must have role of ADMIN.")
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        # Call the regular create_user method with these defaults
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class AccountStatus(models.TextChoices):
        GOOD_STANDING = "GOOD_STANDING", "Good Standing"
        FINES_OWED = "FINES_OWED", "Fines Owed"
        SUSPENDED = "SUSPENDED", "Suspended"

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        MEMBER = "MEMBER", "Member"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    # --- MODIFIED FIELDS ---
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    batch = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=10, blank=True)

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True,
        default="profile_pics/user_avatar.png",
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.GOOD_STANDING,
    )
    is_active = models.BooleanField(default=False)
    # New field to specifically track verification status.
    is_verified = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    library_card = models.OneToOneField(
        "cards.LibraryCard", on_delete=models.SET_NULL, null=True, blank=True
    )
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
