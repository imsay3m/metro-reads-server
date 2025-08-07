from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="e.g., CSE, EEE, BBA")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
