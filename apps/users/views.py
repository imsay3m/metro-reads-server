from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cards.models import LibraryCard
from apps.cards.tasks import generate_library_card_pdf_task

from .models import User
from .permissions import IsAdminOrLibrarian
from .serializers import UserRegistrationSerializer, UserSerializer
from .tasks import send_verification_email_task


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # The API endpoint path for verification
        api_verify_path = reverse("user-verify", kwargs={"uidb64": uid, "token": token})

        # The full URL the user will click, pointing to your FRONTEND
        # Your frontend will receive the uid and token and then call the API path.
        # Example Frontend URL: http://localhost:3000/verify/Mw/c0qjwe-abcd.../
        frontend_verification_url = (
            f"{settings.FRONTEND_BASE_URL}/users/verify/{uid}/{token}/"
        )

        subject = "Welcome to Metro Reads! Please Verify Your Account"
        context = {
            "email_title": "Account Verification",
            "user_name": user.first_name,
            "user_email": user.email,
            "verification_url": frontend_verification_url,
        }

        send_verification_email_task.delay(
            subject, "emails/account_verification.html", context, [user.email]
        )

        response_data = {
            "user_data": serializer.data,
            "detail": "Registration successful. Please check your email to verify your account.",
        }

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class UserVerificationView(APIView):
    """
    API view to handle user account verification from the email link.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # If the token is valid, activate the user
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response(
                {
                    "detail": "Thank you for your email confirmation. You can now log in."
                },
                status=status.HTTP_200_OK,
            )
        else:
            # If the token is invalid or expired
            return Response(
                {"detail": "Activation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving the profile of the currently authenticated user.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the user associated with the request
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing users.
    Provides `list` and `retrieve` actions.
    Admins/Librarians can also generate library cards for users.
    """

    queryset = User.objects.all().select_related("library_card")
    serializer_class = UserSerializer
    permission_classes = [
        IsAdminOrLibrarian
    ]  # Only Admins/Librarians can view user list

    @action(detail=True, methods=["post"], url_path="generate-card")
    def generate_card(self, request, pk=None):
        """
        Generates a new library card for a user.
        If a card already exists, it will be replaced.
        """
        user = self.get_object()

        # If user already has a card, deactivate it before creating a new one.
        if hasattr(user, "library_card") and user.library_card:
            user.library_card.is_active = False
            user.library_card.save()

        # Create a new library card instance
        new_card = LibraryCard.objects.create()

        # Link the card to the user
        user.library_card = new_card
        user.save()

        # Enqueue async PDF generation
        generate_library_card_pdf_task.delay(user.id, str(new_card.id))
        return Response(
            {
                "status": "Library card generation enqueued.",
                "card_id": new_card.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
