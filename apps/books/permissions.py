from rest_framework.permissions import SAFE_METHODS, BasePermission


# Custom permission: Only allow users to modify/delete their own reviews
class IsReviewOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed to the review owner
        return obj.user == request.user
