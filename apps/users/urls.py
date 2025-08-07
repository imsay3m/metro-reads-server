from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserProfileView,
    UserRegistrationView,
    UserVerificationView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"manage", UserViewSet, basename="user-manage")


urlpatterns = [
    # Auth endpoints
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        UserVerificationView.as_view(),
        name="user-verify",
    ),
    path("", include(router.urls)),
]
