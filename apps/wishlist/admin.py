from django.contrib import admin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "added_date"]
    list_filter = ["added_date", "user__role"]
    search_fields = ["user__email", "book__title", "book__author"]
    readonly_fields = ["added_date"]
    ordering = ["-added_date"]
