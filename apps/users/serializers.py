from rest_framework import serializers

from apps.academic.models import Department

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving User information.
    """

    # Use SerializerMethodField to handle the OneToOne relationship gracefully
    library_card_id = serializers.SerializerMethodField()
    department = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "library_card_id",
            "profile_picture",
            "department",
            "student_id",
            "batch",
            "section",
        ]

    def get_library_card_id(self, obj):
        # Return the card ID if it exists, otherwise return None
        return (
            obj.library_card.id
            if hasattr(obj, "library_card") and obj.library_card
            else None
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Users (Registration).
    Handles password hashing.
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "department",
            "student_id",
            "batch",
            "section",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def create(self, validated_data):
        # Use the custom manager's create_user method to handle password hashing
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user
