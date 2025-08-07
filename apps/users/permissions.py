from rest_framework import permissions

from .models import User


class IsAdminOrLibrarian(permissions.BasePermission):
    """
    Custom permission to only allow Admins or Librarians to access a view.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in [User.Role.ADMIN, User.Role.LIBRARIAN]
        )
