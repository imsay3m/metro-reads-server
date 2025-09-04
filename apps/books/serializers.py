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
    cover_image = serializers.URLField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "published_date",
            "total_copies",
            "available_copies",
            "description",
            "publisher",
            "page_count",
            "genres",
            "genre_ids",
            "upload_cover_image",
            "cover_image",
        ]

    def update(self, instance, validated_data):
        # --- START DEBUGGING ---
        print("--- Inside BookSerializer UPDATE method ---")
        print(f"Initial validated_data: {validated_data}")

        image_file = validated_data.pop("upload_cover_image", None)
        print(f"Popped image_file: {image_file}")
        # --- END DEBUGGING ---

        # Perform the standard update for all other fields
        instance = super().update(instance, validated_data)

        if image_file:
            print(">>> Image file exists, attempting to upload to ImgBB...")
            image_url = upload_image_to_imgbb(image_file)

            # --- START DEBUGGING ---
            print(f"URL received from ImgBB: {image_url}")
            # --- END DEBUGGING ---

            if image_url:
                print(f">>> ImgBB URL is valid. Saving '{image_url}' to instance...")
                instance.cover_image = image_url
                instance.save(update_fields=["cover_image"])
            else:
                print(">>> ImgBB URL is None. Skipping save.")

        print(
            f"--- Final instance cover_image before returning: {instance.cover_image} ---"
        )
        return instance

    # Add the same logic to the create method for completeness
    def create(self, validated_data):
        image_file = validated_data.pop("upload_cover_image", None)
        instance = super().create(validated_data)
        if image_file:
            image_url = upload_image_to_imgbb(image_file)
            if image_url:
                instance.cover_image = image_url
                instance.save(update_fields=["cover_image"])
        return instance
