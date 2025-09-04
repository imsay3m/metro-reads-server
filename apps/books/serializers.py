from rest_framework import serializers

from apps.academic.models import Genre
from apps.site_config.utils import upload_image_to_imgbb

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
    upload_cover_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["cover_image"]

    def create(self, validated_data):
        # Pop the upload field before creating the object
        image_file = validated_data.pop("upload_cover_image", None)

        # Create the book instance first
        book = super().create(validated_data)

        # If an image was provided, upload it and update the new object
        if image_file:
            image_url = upload_image_to_imgbb(image_file)
            if image_url:
                book.cover_image = image_url
                book.save()

        return book

    def update(self, instance, validated_data):
        # Pop the upload field before updating the object
        image_file = validated_data.pop("upload_cover_image", None)

        # Update the book instance first
        book = super().update(instance, validated_data)

        # If an image was provided, upload it and update the instance
        if image_file:
            image_url = upload_image_to_imgbb(image_file)
            if image_url:
                book.cover_image = image_url
                book.save()

        return book
