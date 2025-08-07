from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import LibrarySettings

# This file is now only responsible for models within the 'site_config' app.
admin.site.register(LibrarySettings, SingletonModelAdmin)
