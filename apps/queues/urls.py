from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QueueViewSet

router = DefaultRouter()
router.register(r"", QueueViewSet, basename="queue")

urlpatterns = [
    path("", include(router.urls)),
]
