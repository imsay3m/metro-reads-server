from rest_framework import serializers

from apps.academic.models import Department

from .models import User
from apps.site_config.utils import upload_image_to_imgbb


class UserSerializer(serializers.ModelSerializer):
    library_card_id = serializers.SerializerMethodField()
    department = serializers.StringRelatedField(
        read_only=True
    )  # Department is read-only here

    # CORRECTED: Use a distinct name for the upload field
    upload_profile_picture = serializers.ImageField(write_only=True, required=False)

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
            "upload_profile_picture",
        ]
        read_only_fields = ["profile_picture"]

    def get_library_card_id(self, obj):
        return (
            obj.library_card.id
            if hasattr(obj, "library_card") and obj.library_card
            else None
        )

    def update(self, instance, validated_data):
        image_file = validated_data.pop("upload_profile_picture", None)
        user = super().update(instance, validated_data)
        if image_file:
            imgbb_url = upload_image_to_imgbb(image_file)
            if imgbb_url:
                user.profile_picture = imgbb_url
                user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )
    # CORRECTED: Use a distinct name
    upload_profile_picture = serializers.ImageField(write_only=True, required=False)

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
            "upload_profile_picture",  # Use the distinct name
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def create(self, validated_data):
        image_file = validated_data.pop("upload_profile_picture", None)
        # Use the custom manager's create_user method
        user = User.objects.create_user(
            email=validated_data.pop("email"),
            password=validated_data.pop("password"),
            **validated_data
        )
        if image_file:
            imgbb_url = upload_image_to_imgbb(image_file)
            if imgbb_url:
                user.profile_picture = imgbb_url
                user.save()
        return user
