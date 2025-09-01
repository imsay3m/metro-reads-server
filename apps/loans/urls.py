from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FineViewSet, LoanViewSet

router = DefaultRouter()
router.register(r"", LoanViewSet, basename="loan")
router.register(r"fines", FineViewSet, basename="fine")

urlpatterns = [
    path("", include(router.urls)),
]
