from rest_framework import permissions

class IsBuyer(permissions.BasePermission):
    """Allow access only to buyers."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'buyer'


class IsSeller(permissions.BasePermission):
    """Allow access only to sellers."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'


class IsAdmin(permissions.BasePermission):
    """Allow access only to admins."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrSellerForWriteReadOnlyOtherwise(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return (
            user and
            user.is_authenticated and
            user.role in ['admin', 'seller']
        )