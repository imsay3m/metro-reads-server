from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GenreViewSet

router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")

urlpatterns = [
    path("", include(router.urls)),
]
