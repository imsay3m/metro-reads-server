from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    This makes the Department model manageable in the Django admin panel.
    """

    # Fields to display in the list view of all departments
    list_display = ("name", "code")

    # Fields that can be searched
    search_fields = ("name", "code")

    # Fields to use for ordering the list
    ordering = ("name",)
