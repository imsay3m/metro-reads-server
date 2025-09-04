from rest_framework import serializers

from apps.academic.models import Department

from .models import User
from .utils import upload_image_to_imgbb


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
            "phone_number",
            "address",
            "account_status",
        ]

    profile_picture = serializers.ImageField(write_only=True, required=False)

    def get_library_card_id(self, obj):
        # Return the card ID if it exists, otherwise return None
        return (
            obj.library_card.id
            if hasattr(obj, "library_card") and obj.library_card
            else None
        )

    def update(self, instance, validated_data):
        image = validated_data.pop("profile_picture", None)
        if image:
            imgbb_url = upload_image_to_imgbb(image)
            instance.profile_picture = imgbb_url
        return super().update(instance, validated_data)

    def create(self, validated_data):
        image = validated_data.pop("profile_picture", None)
        user = super().create(validated_data)
        if image:
            imgbb_url = upload_image_to_imgbb(image)
            user.profile_picture = imgbb_url
            user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Users (Registration).
    Handles password hashing.
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
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
            "phone_number",
            "address",
            "profile_picture",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    profile_picture = serializers.ImageField(write_only=True, required=False)

    def create(self, validated_data):
        image = validated_data.pop("profile_picture", None)
        user = User.objects.create_user(
            email=validated_data.pop("email"),
            password=validated_data.pop("password"),
            first_name=validated_data.pop("first_name"),
            last_name=validated_data.pop("last_name"),
            **validated_data
        )
        if image:
            imgbb_url = upload_image_to_imgbb(image)
            user.profile_picture = imgbb_url
            user.save()
        return user
