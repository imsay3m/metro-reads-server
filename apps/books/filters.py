import django_filters

from apps.academic.models import Genre

from .models import Book


class BookFilter(django_filters.FilterSet):
    """
    Custom FilterSet for the Book model.
    """

    # This is the key field. It allows filtering by one or more genre slugs.
    # e.g., ?genres=science-fiction&genres=mystery
    genres = django_filters.ModelMultipleChoiceFilter(
        field_name="genres__slug",  # Filter on the 'slug' field of the related Genre model
        to_field_name="slug",  # The field on the Genre model to match against
        queryset=Genre.objects.all(),
    )

    class Meta:
        model = Book
        # Define all fields that can be filtered.
        fields = {
            "author": ["exact"],
            "publisher": ["exact"],
            # The 'genres' field is handled by the custom definition above.
        }
