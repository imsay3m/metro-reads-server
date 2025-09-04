from rest_framework import serializers

from apps.academic.models import Genre
from apps.users.utils import upload_image_to_imgbb

from .models import Book


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        source="genres",
        many=True,
        write_only=True,
        required=False,
    )
    cover_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Book
        fields = "__all__"

    def create(self, validated_data):
        image = validated_data.pop("cover_image", None)
        if image:
            imgbb_url = upload_image_to_imgbb(image)
            validated_data["cover_image"] = imgbb_url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.pop("cover_image", None)
        if image:
            imgbb_url = upload_image_to_imgbb(image)
            validated_data["cover_image"] = imgbb_url
        return super().update(instance, validated_data)
