from django.urls import include, path
from rest_framework_nested import routers

from .views import BookViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

reviews_router = routers.NestedDefaultRouter(router, r"books", lookup="book")
reviews_router.register(r"reviews", ReviewViewSet, basename="book-reviews")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(reviews_router.urls)),
]
