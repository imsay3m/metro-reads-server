from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import LibrarySettings

admin.site.register(LibrarySettings, SingletonModelAdmin)
