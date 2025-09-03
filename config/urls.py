from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Metro Reads API",
        default_version="v1",
        description="API documentation for the Metro Reads Library Management System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@metroreads.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
    # API Documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # App URLs will be added here
    # API Endpoints
    path("api/users/", include("apps.users.urls")),
    path("api/books/", include("apps.books.urls")),
    path("api/loans/", include("apps.loans.urls")),
    path("api/queues/", include("apps.queues.urls")),
    path("api/academic/", include("apps.academic.urls")),
    path("api/wishlist/", include("apps.wishlist.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
