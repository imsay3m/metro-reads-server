from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import Genre
from apps.books.models import Book

from .models import Wishlist

User = get_user_model()


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.genre = Genre.objects.create(name="Fiction", slug="fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date="2023-01-01",
            total_copies=1,
            available_copies=1,
        )
        self.book.genres.add(self.genre)

    def test_wishlist_creation(self):
        """Test creating a wishlist item"""
        wishlist_item = Wishlist.objects.create(
            user=self.user, book=self.book, notes="Want to read this"
        )

        self.assertEqual(wishlist_item.user, self.user)
        self.assertEqual(wishlist_item.book, self.book)
        self.assertEqual(wishlist_item.notes, "Want to read this")
        self.assertIsNotNone(wishlist_item.added_date)

    def test_unique_user_book_constraint(self):
        """Test that a user can't add the same book twice to wishlist"""
        Wishlist.objects.create(user=self.user, book=self.book)

        with self.assertRaises(Exception):
            Wishlist.objects.create(user=self.user, book=self.book)


class WishlistAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.genre = Genre.objects.create(name="Fiction", slug="fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            published_date="2023-01-01",
            total_copies=1,
            available_copies=1,
        )
        self.book.genres.add(self.genre)

        self.client.force_authenticate(user=self.user)

    def test_create_wishlist_item(self):
        """Test adding a book to wishlist"""
        url = reverse("wishlist-list")
        data = {"book_id": self.book.id, "notes": "Want to read this"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wishlist.objects.count(), 1)
        self.assertEqual(Wishlist.objects.first().user, self.user)
        self.assertEqual(Wishlist.objects.first().book, self.book)

    def test_duplicate_wishlist_item(self):
        """Test that adding the same book twice returns an error"""
        Wishlist.objects.create(user=self.user, book=self.book)

        url = reverse("wishlist-list")
        data = {"book_id": self.book.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already in your wishlist", response.data["detail"])

    def test_list_wishlist_items(self):
        """Test retrieving user's wishlist"""
        Wishlist.objects.create(user=self.user, book=self.book, notes="Test note")

        url = reverse("wishlist-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["book"]["title"], "Test Book")

    def test_delete_wishlist_item(self):
        """Test removing a book from wishlist"""
        wishlist_item = Wishlist.objects.create(user=self.user, book=self.book)

        url = reverse("wishlist-detail", kwargs={"pk": wishlist_item.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Wishlist.objects.count(), 0)
